from app.agent.llm_provider import LLMProvider, detect_language, extract_json
from app.agent.prompts import ROUTER_SYSTEM_EN, ROUTER_SYSTEM_RU, ROUTER_USER

VALID_CATEGORIES = {"Database", "API", "Reports", "Auth", "UI", "Network", "Other"}
VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_TEAMS = {"backend-db", "backend-api", "frontend", "infra"}


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
        lang = detect_language(f"{title}\n{description}")
        system = ROUTER_SYSTEM_RU if lang == "ru" else ROUTER_SYSTEM_EN
        user = ROUTER_USER.format(title=title, description=description)
        prompt = f"{system}\n\n{user}"

        raw = await self.llm.generate(prompt)
        data = extract_json(raw or "")
        if not data:
            return RouteResult()

        category = str(data.get("category") or "Other")
        priority = str(data.get("priority") or "medium").lower()
        team = str(data.get("assigned_team") or "backend-api").lower()

        if category not in VALID_CATEGORIES:
            category = "Other"
        if priority not in VALID_PRIORITIES:
            priority = "medium"
        if team not in VALID_TEAMS:
            team = "backend-api"

        return RouteResult(
            category=category, priority=priority, assigned_team=team
        )
