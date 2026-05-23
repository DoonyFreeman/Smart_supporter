from app.agent.llm_provider import LLMProvider
from app.agent.matcher import MatchResult
from app.agent.prompts import CLASSIFICATION_PROMPT

CLASSIFICATION_TYPES = ["faq_match", "bug", "feature_request", "needs_info"]


class TicketClassifier:
    def __init__(self, stub: bool = True) -> None:
        self.llm = LLMProvider(stub=stub)

    async def classify(self, title: str, description: str, matches: MatchResult) -> str:
        prompt = CLASSIFICATION_PROMPT.format(
            title=title,
            description=description,
            similar_tickets="\n".join(matches.similar_tickets) or "none",
            faq_articles="\n".join(matches.faq_articles) or "none",
        )

        result = await self.llm.generate(prompt)
        result = result.strip().lower()

        if result in CLASSIFICATION_TYPES:
            return result
        if "faq_match" in result:
            return "faq_match"
        if "bug" in result:
            return "bug"
        return "needs_info"
