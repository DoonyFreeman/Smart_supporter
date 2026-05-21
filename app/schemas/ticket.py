from datetime import datetime

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)


class TicketUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, min_length=1)
    status: str | None = None
    priority: str | None = None
    category: str | None = None
    assigned_team: str | None = None
    assigned_to: int | None = None
    response_text: str | None = None


class TicketResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    description: str
    status: str
    priority: str | None
    category: str | None
    assigned_team: str | None
    assigned_to: int | None
    created_by: int
    response_text: str | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime
