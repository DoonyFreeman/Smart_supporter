from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.ticket_history import TicketHistory


class TicketStatus(str, enum.Enum):
    NEW = "new"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    TRIAGED = "triaged"
    NEEDS_INFO = "needs_info"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[TicketStatus] = mapped_column(
        String(20), default=TicketStatus.NEW, server_default=TicketStatus.NEW.value
    )
    priority: Mapped[TicketPriority | None] = mapped_column(String(20), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    creator: Mapped["User"] = relationship(
        back_populates="tickets", foreign_keys=[created_by]
    )
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assigned_to])
    history: Mapped[list["TicketHistory"]] = relationship(
        back_populates="ticket", cascade="all, delete-orphan"
    )
