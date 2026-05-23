import json
import re

from app.agent.llm_provider import LLMProvider
from app.agent.prompts import ROUTING_PROMPT


class RouteResult:
    def __init__(
        self,
        category: str = "Other",
        priority: str = "medium",
        assigned_team: str = "backend-api",
    ) -> None:
        self.category = category
        self.priority = priority
        self.assigned_team = assigned_team


class TicketRouter:
    def __init__(self, stub: bool = True) -> None:
        self.llm = LLMProvider(stub=stub)

    async def route(self, title: str, description: str) -> RouteResult:
        prompt = ROUTING_PROMPT.format(title=title, description=description)
        result = await self.llm.generate(prompt)

        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", result, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                return RouteResult()

        return RouteResult(
            category=data.get("category", "Other"),
            priority=data.get("priority", "medium"),
            assigned_team=data.get("assigned_team", "backend-api"),
        )
