from fastapi import APIRouter, Query, status
from sqlalchemy import select

from app.api.deps import AdminUser, CurrentUser, DB, Pagination
from app.models import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.utils.errors import ForbiddenException, NotFoundException

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    db: DB,
    payload: TicketCreate,
    current_user: CurrentUser,
) -> Ticket:
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        created_by=current_user.id,
    )
    db.add(ticket)
    await db.flush()
    await db.refresh(ticket)
    return ticket


@router.post(
    "/submit", response_model=TicketResponse, status_code=status.HTTP_201_CREATED
)
async def submit_ticket(
    db: DB,
    payload: TicketCreate,
    current_user: CurrentUser,
) -> Ticket:
    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        status=TicketStatus.PROCESSING,
        created_by=current_user.id,
    )
    db.add(ticket)
    await db.flush()
    await db.refresh(ticket)
    return ticket


@router.get("/", response_model=list[TicketResponse])
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
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    db: DB,
    ticket_id: int,
    current_user: CurrentUser,
) -> Ticket:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise NotFoundException("Ticket not found")
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    db: DB,
    ticket_id: int,
    payload: TicketUpdate,
    current_user: CurrentUser,
) -> Ticket:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise NotFoundException("Ticket not found")

    if (
        current_user.role not in ("admin", "agent")
        and ticket.created_by != current_user.id
    ):
        raise ForbiddenException("Not authorized to update this ticket")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ticket, field, value)

    await db.flush()
    await db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ticket(
    db: DB,
    ticket_id: int,
    admin: AdminUser,
) -> None:
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise NotFoundException("Ticket not found")

    await db.delete(ticket)
