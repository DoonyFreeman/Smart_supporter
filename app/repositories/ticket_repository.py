from sqlalchemy import select

from app.models import Ticket
from app.repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    model_class = Ticket

    async def list_with_filters(
        self,
        status: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        assigned_team: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Ticket]:
        query = select(Ticket)

        if status:
            query = query.where(Ticket.status == status)
        if priority:
            query = query.where(Ticket.priority == priority)
        if category:
            query = query.where(Ticket.category == category)
        if assigned_team:
            query = query.where(Ticket.assigned_team == assigned_team)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def find_similar_by_text(self, text: str, limit: int = 5) -> list[Ticket]:
        query = select(Ticket).where(Ticket.description.ilike(f"%{text}%")).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
