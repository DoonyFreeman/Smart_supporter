from app.agent.llm_provider import LLMProvider, detect_language
from app.agent.matcher import MatchResult
from app.agent.prompts import (
    CLASSIFIER_SYSTEM_EN,
    CLASSIFIER_SYSTEM_RU,
    CLASSIFIER_USER,
)

CLASSIFICATION_TYPES = ["faq_match", "bug", "feature_request", "needs_info"]


def _build_prompt(title: str, description: str, matches: MatchResult) -> str:
    lang = detect_language(f"{title}\n{description}")
    system = CLASSIFIER_SYSTEM_RU if lang == "ru" else CLASSIFIER_SYSTEM_EN
    user = CLASSIFIER_USER.format(
        title=title,
        description=description,
        similar_tickets="\n".join(f"- {t}" for t in matches.similar_tickets)
        or "(none)",
        faq_articles="\n".join(f"- {a}" for a in matches.faq_articles) or "(none)",
        doc_articles="\n".join(f"- {d}" for d in matches.doc_articles) or "(none)",
    )
    return f"{system}\n\n{user}"


class TicketClassifier:
    def __init__(self, stub: bool = True) -> None:
        self.llm = LLMProvider(stub=stub)

    async def classify(
        self, title: str, description: str, matches: MatchResult
    ) -> str:
        prompt = _build_prompt(title, description, matches)
        raw = await self.llm.generate(prompt)
        text = (raw or "").strip().lower().strip(".,'\"` \n\t")

        if text in CLASSIFICATION_TYPES:
            return text
        if "faq_match" in text:
            return "faq_match"
        if "feature_request" in text or "feature request" in text:
            return "feature_request"
        if "bug" in text:
            return "bug"
        return "needs_info"
