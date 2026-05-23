from app.agent.llm_provider import LLMProvider
from app.agent.matcher import MatchResult
from app.agent.prompts import RESPONSE_PROMPT


class ResponseGenerator:
    def __init__(self, stub: bool = True) -> None:
        self.llm = LLMProvider(stub=stub)

    async def generate(
        self,
        title: str,
        description: str,
        ticket_type: str,
        matches: MatchResult,
    ) -> str:
        faq_content = (
            "\n".join(matches.faq_articles) if matches.faq_articles else "none"
        )

        prompt = RESPONSE_PROMPT.format(
            title=title,
            description=description,
            ticket_type=ticket_type,
            faq_content=faq_content,
        )

        return await self.llm.generate(prompt)
