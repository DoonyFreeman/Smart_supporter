from typing import Annotated

from fastapi import Depends, Query
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, UserRole
from app.utils.errors import ForbiddenException, UnauthorizedException
from app.utils.security import decode_token, oauth2_scheme

DB = Annotated[AsyncSession, Depends(get_db)]
Pagination = Annotated[int, Query(ge=1, le=100)]


async def get_current_user(
    db: DB,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise UnauthorizedException("Could not validate credentials")
        sub = payload.get("sub")
        if sub is None:
            raise UnauthorizedException("Could not validate credentials")
        user_id = int(sub)
    except (JWTError, ValueError, TypeError):
        raise UnauthorizedException("Could not validate credentials")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedException("User not found")
    return user


async def get_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin access required")
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]
