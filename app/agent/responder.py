from app.agent.llm_provider import LLMProvider, detect_language
from app.agent.matcher import MatchResult
from app.agent.prompts import (
    RESPONDER_SYSTEM_EN,
    RESPONDER_SYSTEM_RU,
    RESPONDER_USER,
)


class ResponseGenerator:
    def __init__(self, stub: bool = True) -> None:
        self.llm = LLMProvider(stub=stub)

    async def generate(
        self,
        title: str,
        description: str,
        ticket_type: str,
        matches: MatchResult,
        priority: str | None = None,
    ) -> str:
        lang = detect_language(f"{title}\n{description}")
        system = RESPONDER_SYSTEM_RU if lang == "ru" else RESPONDER_SYSTEM_EN

        faq_content = (
            "\n".join(f"- {a}" for a in matches.faq_articles[:3])
            if matches.faq_articles
            else "(none)"
        )
        user = RESPONDER_USER.format(
            title=title,
            description=description,
            ticket_type=ticket_type,
            priority=priority or "n/a",
            faq_content=faq_content,
        )
        prompt = f"{system}\n\n{user}"
        return await self.llm.generate(prompt)
