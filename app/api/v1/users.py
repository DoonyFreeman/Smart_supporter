from fastapi import APIRouter, status

from app.api.deps import AdminUser, CurrentUser, DB, Pagination
from app.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.services import UserService
from app.utils.errors import ForbiddenException

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: DB,
    admin: AdminUser,
    skip: int = 0,
    limit: Pagination = 20,
) -> list[User]:
    service = UserService(db)
    return await service.list_users(skip=skip, limit=limit)


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
    service = UserService(db)
    return await service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    db: DB,
    user_id: int,
    payload: UserUpdate,
    current_user: CurrentUser,
) -> User:
    if current_user.id != user_id and current_user.role != "admin":
        raise ForbiddenException("Not authorized to update this user")
    service = UserService(db)
    return await service.update_user(user_id, payload.model_dump(exclude_unset=True))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: DB,
    user_id: int,
    admin: AdminUser,
) -> None:
    service = UserService(db)
    await service.delete_user(user_id)
