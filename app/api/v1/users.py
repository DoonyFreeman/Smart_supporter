from fastapi import APIRouter, status
from sqlalchemy import select

from app.api.deps import AdminUser, CurrentUser, DB, Pagination
from app.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.utils.errors import ForbiddenException, NotFoundException

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: DB,
    admin: AdminUser,
    skip: int = 0,
    limit: Pagination = 20,
) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser) -> User:
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    db: DB,
    user_id: int,
    current_user: CurrentUser,
) -> User:
    if current_user.id != user_id and current_user.role != "admin":
        raise ForbiddenException("Not authorized to view this user")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    db: DB,
    user_id: int,
    payload: UserUpdate,
    current_user: CurrentUser,
) -> User:
    if current_user.id != user_id and current_user.role != "admin":
        raise ForbiddenException("Not authorized to update this user")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.flush()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: DB,
    user_id: int,
    admin: AdminUser,
) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundException("User not found")

    await db.delete(user)
