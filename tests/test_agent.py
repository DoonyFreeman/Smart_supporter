from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.classifier import TicketClassifier
from app.agent.llm_provider import LLMProvider
from app.agent.matcher import MatchResult, SemanticMatcher
from app.agent.responder import ResponseGenerator
from app.agent.router import RouteResult, TicketRouter
from app.models import DocumentationArticle, FAQArticle, Ticket, TicketStatus, User
from app.services.agent_service import AgentService


@pytest.fixture
def match_result() -> MatchResult:
    return MatchResult(
        similar_tickets=["Ticket 1: Database connection timeout error"],
        faq_articles=["FAQ: How to reset DB connection pool"],
        doc_articles=[],
    )


class TestSemanticMatcher:
    async def test_find_similar_no_data(
        self, db_session: AsyncSession
    ) -> None:
        matcher = SemanticMatcher(db_session)
        result = await matcher.find_similar("database timeout")
        assert isinstance(result, MatchResult)
        assert result.similar_tickets == []
        assert result.faq_articles == []
        assert result.doc_articles == []

    async def test_find_similar_with_data(
        self, db_session: AsyncSession, registered_user: User
    ) -> None:
        ticket = Ticket(
            title="DB timeout",
            description="Cannot connect to database, getting timeout",
            created_by=registered_user.id,
            status=TicketStatus.RESOLVED,
        )
        faq = FAQArticle(
            title="DB Connection Issues",
            content="How to resolve database connection timeouts",
            keywords="database, timeout, connection",
            category="Database",
        )
        doc = DocumentationArticle(
            title="PostgreSQL Setup",
            content="Steps to configure PostgreSQL connection",
            product_area="Database",
        )
        db_session.add_all([ticket, faq, doc])
        await db_session.flush()

        matcher = SemanticMatcher(db_session)
        result = await matcher.find_similar("database")
        assert len(result.similar_tickets) > 0
        assert len(result.faq_articles) > 0
        assert len(result.doc_articles) > 0


class TestTicketClassifier:
    async def test_classify_with_stub(self, match_result: MatchResult) -> None:
        classifier = TicketClassifier(stub=True)
        result = await classifier.classify("Test ticket", "Description", match_result)
        assert result == "needs_info"

    async def test_classify_bug(self, match_result: MatchResult) -> None:
        classifier = TicketClassifier(stub=True)
        classifier.llm = AsyncMock(spec=LLMProvider)
        classifier.llm.generate = AsyncMock(return_value="bug")

        result = await classifier.classify("API error 500", "Server error", match_result)
        assert result == "bug"

    async def test_classify_faq_match(self, match_result: MatchResult) -> None:
        classifier = TicketClassifier(stub=True)
        classifier.llm = AsyncMock(spec=LLMProvider)
        classifier.llm.generate = AsyncMock(return_value="faq_match")

        result = await classifier.classify(
            "How to reset password", "Forgot my password", match_result
        )
        assert result == "faq_match"

    async def test_classify_feature_request(self, match_result: MatchResult) -> None:
        classifier = TicketClassifier(stub=True)
        classifier.llm = AsyncMock(spec=LLMProvider)
        classifier.llm.generate = AsyncMock(return_value="feature_request")

        result = await classifier.classify(
            "Add dark mode", "Would like dark theme support", match_result
        )
        assert result == "feature_request"


class TestTicketRouter:
    async def test_route_with_stub(self) -> None:
        router = TicketRouter(stub=True)
        result = await router.route("API error", "Getting 500 on /users")
        assert isinstance(result, RouteResult)
        assert result.category == "Other"
        assert result.priority == "medium"
        assert result.assigned_team == "backend-api"

    async def test_route_with_mocked_llm(self) -> None:
        router = TicketRouter(stub=True)
        router.llm = AsyncMock(spec=LLMProvider)
        router.llm.generate = AsyncMock(
            return_value='{"category": "API", "priority": "high", "assigned_team": "backend-api"}'
        )

        result = await router.route("API error", "Getting 500")
        assert result.category == "API"
        assert result.priority == "high"
        assert result.assigned_team == "backend-api"

    async def test_route_with_extra_text(self) -> None:
        router = TicketRouter(stub=True)
        router.llm = AsyncMock(spec=LLMProvider)
        router.llm.generate = AsyncMock(
            return_value='Here is the result: {"category": "Network", "priority": "critical", "assigned_team": "infra"}'
        )

        result = await router.route("Network down", "All services unavailable")
        assert result.category == "Network"
        assert result.priority == "critical"
        assert result.assigned_team == "infra"

    async def test_route_with_garbage_response(self) -> None:
        router = TicketRouter(stub=True)
        router.llm = AsyncMock(spec=LLMProvider)
        router.llm.generate = AsyncMock(return_value="garbage response")

        result = await router.route("Test", "Description")
        assert isinstance(result, RouteResult)
        assert result.category == "Other"


class TestResponseGenerator:
    async def test_generate_with_stub(self, match_result: MatchResult) -> None:
        generator = ResponseGenerator(stub=True)
        result = await generator.generate(
            "Test ticket", "Description", "bug", match_result
        )
        assert result == "stub"

    async def test_generate_with_mocked_llm(self, match_result: MatchResult) -> None:
        generator = ResponseGenerator(stub=True)
        generator.llm = AsyncMock(spec=LLMProvider)
        expected = "We have identified your issue and are working on a fix."
        generator.llm.generate = AsyncMock(return_value=expected)

        result = await generator.generate(
            "Bug report", "App crashes on login", "bug", match_result
        )
        assert result == expected


class TestAgentService:
    async def test_process_ticket_nonexistent(
        self, db_session: AsyncSession
    ) -> None:
        service = AgentService(db_session)
        await service.process_ticket(99999)

    async def test_process_ticket_full_flow(
        self, db_session: AsyncSession, registered_user: User
    ) -> None:
        ticket = Ticket(
            title="DB connection timeout",
            description="Cannot connect to PostgreSQL database",
            created_by=registered_user.id,
        )
        db_session.add(ticket)
        await db_session.flush()

        service = AgentService(db_session)
        await service.process_ticket(ticket.id)

        await db_session.refresh(ticket)
        assert ticket.response_text is not None
        assert ticket.status in (
            TicketStatus.RESOLVED,
            TicketStatus.TRIAGED,
            TicketStatus.NEEDS_INFO,
        )
