from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 20


class PaginatedResponse(BaseModel):
    items: list
    total: int
    skip: int
    limit: int
