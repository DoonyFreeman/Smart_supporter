from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DocumentationArticle, FAQArticle, Ticket, TicketStatus
from app.repositories import (
    DocumentationRepository,
    FAQRepository,
    TicketRepository,
)

# Multilingual stop-words — kept small on purpose so we don't drop signal.
_STOP_WORDS = {
    # English
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "do", "does", "doing",
    "for", "from", "have", "has", "had", "he", "her", "his", "i", "in", "is", "it",
    "its", "me", "my", "no", "not", "of", "on", "or", "our", "out", "she", "so",
    "than", "that", "the", "their", "them", "then", "there", "these", "they",
    "this", "to", "was", "we", "were", "what", "when", "where", "which", "who",
    "why", "will", "with", "you", "your", "can", "cannot", "would", "should",
    "could", "may", "might", "if", "into", "about", "very", "just", "too", "also",
    "any", "all", "some", "more", "most", "such", "only", "own", "same",
    # Russian
    "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то",
    "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
    "бы", "по", "только", "ее", "мне", "было", "вот", "от", "меня", "еще",
    "нет", "о", "из", "ему", "теперь", "когда", "даже", "ну", "вдруг", "ли",
    "если", "уже", "или", "ни", "быть", "был", "него", "до", "вас", "нибудь",
    "опять", "уж", "вам", "ведь", "там", "потом", "себя", "ничего", "ей",
    "может", "они", "тут", "где", "есть", "надо", "ней", "для", "мы", "тебя",
    "их", "чем", "была", "сам", "чтоб", "без", "будто", "чего", "раз", "тоже",
    "себе", "под", "будет", "ж", "тогда", "кто", "этот", "того", "потому",
    "этого", "какой", "совсем", "ним", "здесь", "этом", "один", "почти", "мой",
    "тем", "чтобы", "нее", "сейчас", "были", "куда", "зачем", "всех", "никогда",
    "можно", "при", "наконец", "два", "об", "другой", "хоть", "после", "над",
    "больше", "тот", "через", "эти", "нас", "про", "всего", "них", "какая",
    "много", "разве", "сказала", "три", "эту", "моя", "впрочем", "хорошо",
    "свою", "этой", "перед", "иногда", "лучше", "чуть", "том", "нельзя", "такой",
    "ним", "всю", "конечно", "всё",
}

_WORD_RE = re.compile(r"[A-Za-zЀ-ӿ0-9_]{2,}")


def extract_keywords(text: str, top_n: int = 8) -> list[str]:
    """Return the most informative tokens from a ticket text.

    Lowercases, strips stop-words, prefers tokens with digits or length >= 4
    (better signal-to-noise for a tech-support corpus).
    """
    if not text:
        return []
    tokens = [t.lower() for t in _WORD_RE.findall(text)]
    tokens = [
        t
        for t in tokens
        if t not in _STOP_WORDS and (len(t) >= 4 or any(c.isdigit() for c in t))
    ]
    if not tokens:
        return []
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(top_n)]


@dataclass
class MatchResult:
    similar_tickets: list[str] = field(default_factory=list)
    faq_articles: list[str] = field(default_factory=list)
    doc_articles: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


class SemanticMatcher:
    """Keyword-based retrieval over tickets / FAQ / documentation.

    Not "semantic" in the embeddings sense (yet), but uses lemma-ish keyword
    matching with stop-word filtering and OR across keywords so it's far more
    robust than a single substring ILIKE on the raw text.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.ticket_repo = TicketRepository(db)
        self.faq_repo = FAQRepository(db)
        self.doc_repo = DocumentationRepository(db)

    async def find_similar(self, text: str) -> MatchResult:
        keywords = extract_keywords(text)

        # Backward-compat: if extraction yielded nothing (very short text),
        # fall through to the raw text so the old simple-search behavior
        # still finds substring matches (used in tests).
        if not keywords:
            tickets = await self.ticket_repo.find_similar_by_text(text)
            faqs = await self.faq_repo.search_by_keywords(text)
            docs = await self.doc_repo.search_by_product_area(text)
        else:
            tickets = await self._search_tickets(keywords)
            faqs = await self._search_faqs(keywords)
            docs = await self._search_docs(keywords)

        return MatchResult(
            similar_tickets=[
                self._render(t.title, t.description, 220) for t in tickets[:5]
            ],
            faq_articles=[
                self._render(a.title, a.content, 280) for a in faqs[:5]
            ],
            doc_articles=[
                self._render(d.title, d.content, 220) for d in docs[:3]
            ],
            keywords=keywords,
        )

    async def _search_tickets(self, keywords: list[str]) -> list[Ticket]:
        clauses = [
            func.lower(Ticket.description).contains(kw) for kw in keywords
        ] + [func.lower(Ticket.title).contains(kw) for kw in keywords]
        if not clauses:
            return []
        stmt = (
            select(Ticket)
            .where(
                or_(*clauses),
                Ticket.status.in_(
                    [
                        TicketStatus.RESOLVED.value,
                        TicketStatus.CLOSED.value,
                        TicketStatus.TRIAGED.value,
                    ]
                ),
            )
            .limit(10)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _search_faqs(self, keywords: list[str]) -> list[FAQArticle]:
        clauses = []
        for kw in keywords:
            clauses.append(func.lower(FAQArticle.keywords).contains(kw))
            clauses.append(func.lower(FAQArticle.title).contains(kw))
            clauses.append(func.lower(FAQArticle.content).contains(kw))
        if not clauses:
            return []
        stmt = select(FAQArticle).where(or_(*clauses)).limit(10)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _search_docs(
        self, keywords: list[str]
    ) -> list[DocumentationArticle]:
        clauses = []
        for kw in keywords:
            clauses.append(func.lower(DocumentationArticle.product_area).contains(kw))
            clauses.append(func.lower(DocumentationArticle.title).contains(kw))
            clauses.append(func.lower(DocumentationArticle.content).contains(kw))
        if not clauses:
            return []
        stmt = select(DocumentationArticle).where(or_(*clauses)).limit(10)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def _render(title: str, body: str, body_len: int) -> str:
        body = (body or "").strip().replace("\n", " ")
        if len(body) > body_len:
            body = body[:body_len].rstrip() + "…"
        return f"{title}: {body}"
