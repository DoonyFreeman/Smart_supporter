import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent import heuristics
from app.agent.classifier import TicketClassifier
from app.agent.llm_provider import detect_language
from app.agent.matcher import MatchResult, SemanticMatcher
from app.agent.responder import ResponseGenerator
from app.agent.router import TicketRouter
from app.config import settings
from app.models import TicketPriority, TicketStatus
from app.repositories import TicketRepository

logger = logging.getLogger(__name__)


class AgentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.ticket_repo = TicketRepository(db)
        self.matcher = SemanticMatcher(db)
        stub = settings.LLM_STUB
        self.classifier = TicketClassifier(stub=stub)
        self.router = TicketRouter(stub=stub)
        self.responder = ResponseGenerator(stub=stub)

    async def process_ticket(self, ticket_id: int) -> None:
        ticket = await self.ticket_repo.get(ticket_id)
        if not ticket:
            return

        ticket.status = TicketStatus.PROCESSING
        await self.db.flush()

        try:
            matches = await self.matcher.find_similar(
                f"{ticket.title}\n{ticket.description}"
            )
        except Exception:
            logger.exception("matcher failed for ticket %s", ticket_id)
            matches = MatchResult()

        ticket_type = await self._classify(ticket.title, ticket.description, matches)

        priority_value: str | None = None
        if ticket_type == "faq_match":
            ticket.status = TicketStatus.RESOLVED
        elif ticket_type in ("bug", "feature_request"):
            category, priority, team = await self._route(
                ticket.title, ticket.description
            )
            ticket.category = category
            ticket.priority = TicketPriority(priority)
            ticket.assigned_team = team
            ticket.status = TicketStatus.TRIAGED
            priority_value = priority
        else:
            ticket.status = TicketStatus.NEEDS_INFO

        ticket.response_text = await self._respond(
            ticket.title,
            ticket.description,
            ticket_type,
            matches,
            priority_value,
        )

        if ticket.status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.now(timezone.utc)

        await self.db.flush()

    async def _classify(
        self, title: str, description: str, matches: MatchResult
    ) -> str:
        try:
            return await self.classifier.classify(title, description, matches)
        except Exception as exc:
            logger.warning("LLM classify failed, using heuristic: %s", exc)
            return heuristics.classify(title, description, matches)

    async def _route(
        self, title: str, description: str
    ) -> tuple[str, str, str]:
        try:
            result = await self.router.route(title, description)
            return result.category, result.priority, result.assigned_team
        except Exception as exc:
            logger.warning("LLM route failed, using heuristic: %s", exc)
            return heuristics.route(title, description)

    async def _respond(
        self,
        title: str,
        description: str,
        ticket_type: str,
        matches: MatchResult,
        priority: str | None,
    ) -> str:
        try:
            text = await self.responder.generate(
                title, description, ticket_type, matches, priority=priority
            )
            if text and text.strip() and text.strip() != "stub":
                return text
        except Exception as exc:
            logger.warning("LLM respond failed, using heuristic: %s", exc)
        lang = detect_language(f"{title}\n{description}")
        return heuristics.response(ticket_type, lang, matches)
