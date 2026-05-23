from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import (
    DocumentationRepository,
    FAQRepository,
    TicketRepository,
)


class MatchResult:
    def __init__(
        self,
        similar_tickets: list[str] = [],
        faq_articles: list[str] = [],
        doc_articles: list[str] = [],
    ) -> None:
        self.similar_tickets = similar_tickets
        self.faq_articles = faq_articles
        self.doc_articles = doc_articles


class SemanticMatcher:
    def __init__(self, db: AsyncSession) -> None:
        self.ticket_repo = TicketRepository(db)
        self.faq_repo = FAQRepository(db)
        self.doc_repo = DocumentationRepository(db)

    async def find_similar(self, text: str) -> MatchResult:
        tickets = await self.ticket_repo.find_similar_by_text(text)
        faq = await self.faq_repo.search_by_keywords(text)
        docs = await self.doc_repo.search_by_product_area(text)

        return MatchResult(
            similar_tickets=[f"{t.title}: {t.description[:200]}" for t in tickets],
            faq_articles=[f"{a.title}: {a.content[:200]}" for a in faq],
            doc_articles=[f"{d.title}: {d.content[:200]}" for d in docs],
        )
