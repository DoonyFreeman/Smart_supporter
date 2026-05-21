from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

DB = Annotated[AsyncSession, Depends(get_db)]
Pagination = Annotated[int, Query(ge=1, le=100, default=20)]
