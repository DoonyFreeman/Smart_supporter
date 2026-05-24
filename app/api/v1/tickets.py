from fastapi import APIRouter, Query, status

from app.api.deps import AdminUser, CurrentUser, DB, Pagination
from app.models import Ticket
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.services import TicketService
from app.tasks import process_ticket
from app.utils.errors import ForbiddenException

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    db: DB,
    payload: TicketCreate,
    current_user: CurrentUser,
) -> Ticket:
    service = TicketService(db)
    return await service.create_ticket(
        title=payload.title,
        description=payload.description,
        created_by=current_user.id,
    )


@router.post(
    "/submit", response_model=TicketResponse, status_code=status.HTTP_201_CREATED
)
async def submit_ticket(

    db: DB,
    payload: TicketCreate,
    current_user: CurrentUser,
) -> Ticket:
    service = TicketService(db)
    ticket = await service.submit_ticket(
        title=payload.title,
        description=payload.description,
        created_by=current_user.id,
    )
    process_ticket.delay(ticket.id)
    return ticket


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    db: DB,
    current_user: CurrentUser,
    status: str | None = Query(None),
    priority: str | None = Query(None),
    category: str | None = Query(None),
    assigned_team: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: Pagination = 20,
) -> list[Ticket]:
    service = TicketService(db)
    return await service.list_tickets(
        status=status,
        priority=priority,
        category=category,
        assigned_team=assigned_team,
        skip=skip,
        limit=limit,
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    db: DB,
    ticket_id: int,
    current_user: CurrentUser,
) -> Ticket:
    service = TicketService(db)
    return await service.get_ticket(ticket_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    db: DB,
    ticket_id: int,
    payload: TicketUpdate,
    current_user: CurrentUser,
) -> Ticket:
    service = TicketService(db)
    ticket = await service.get_ticket(ticket_id)
    if (
        current_user.role not in ("admin", "agent")
        and ticket.created_by != current_user.id
    ):
        raise ForbiddenException("Not authorized to update this ticket")
    return await service.update_ticket(
        ticket_id, payload.model_dump(exclude_unset=True)
    )


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    db: DB,
    ticket_id: int,
    admin: AdminUser,
) -> None:
    service = TicketService(db)
    await service.delete_ticket(ticket_id)
