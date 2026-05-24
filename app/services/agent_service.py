from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.classifier import TicketClassifier
from app.agent.matcher import SemanticMatcher
from app.agent.responder import ResponseGenerator
from app.agent.router import TicketRouter
from app.config import settings
from app.models import TicketPriority, TicketStatus
from app.repositories import TicketRepository


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

        try:
            matches = await self.matcher.find_similar(ticket.description)

            ticket_type = await self.classifier.classify(
                ticket.title, ticket.description, matches
            )

            if ticket_type == "faq_match":
                ticket.status = TicketStatus.RESOLVED
            elif ticket_type in ("bug", "feature_request"):
                route = await self.router.route(ticket.title, ticket.description)
                ticket.category = route.category
                ticket.priority = TicketPriority(route.priority)
                ticket.assigned_team = route.assigned_team
                ticket.status = TicketStatus.TRIAGED
            else:
                ticket.status = TicketStatus.NEEDS_INFO

            ticket.response_text = await self.responder.generate(
                ticket.title, ticket.description, ticket_type, matches
            )

            if ticket.status == TicketStatus.RESOLVED:
                ticket.resolved_at = datetime.now(timezone.utc)
        except Exception:
            ticket.status = TicketStatus.NEEDS_INFO
            ticket.response_text = (
                "The ticket could not be processed automatically due to an internal error. "
                "A support agent will review it manually."
            )

        await self.db.flush()
