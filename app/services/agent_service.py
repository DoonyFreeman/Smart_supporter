from sqlalchemy.ext.asyncio import AsyncSession


class AgentService:
    def __init__(self, db: AsyncSession) -> None:
        pass

    async def process_ticket(self, ticket_id: int) -> None:
        pass
