from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ticket, TicketStatus
from app.repositories import TicketRepository
from app.utils.errors import NotFoundException


class TicketService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = TicketRepository(db)

    async def create_ticket(
        self, title: str, description: str, created_by: int
    ) -> Ticket:
        ticket = Ticket(
            title=title,
            description=description,
            created_by=created_by,
        )
        return await self.repo.create(ticket)

    async def submit_ticket(
        self, title: str, description: str, created_by: int
    ) -> Ticket:
        ticket = Ticket(
            title=title,
            description=description,
            status=TicketStatus.PROCESSING,
            created_by=created_by,
        )
        return await self.repo.create(ticket)

    async def list_tickets(
        self,
        status: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        assigned_team: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Ticket]:
        return await self.repo.list_with_filters(
            status=status,
            priority=priority,
            category=category,
            assigned_team=assigned_team,
            skip=skip,
            limit=limit,
        )

    async def get_ticket(self, ticket_id: int) -> Ticket:
        ticket = await self.repo.get(ticket_id)
        if not ticket:
            raise NotFoundException("Ticket not found")
        return ticket

    async def update_ticket(self, ticket_id: int, data: dict) -> Ticket:
        ticket = await self.repo.update(ticket_id, data)
        if not ticket:
            raise NotFoundException("Ticket not found")
        return ticket

    async def delete_ticket(self, ticket_id: int) -> None:
        deleted = await self.repo.delete(ticket_id)
        if not deleted:
            raise NotFoundException("Ticket not found")
