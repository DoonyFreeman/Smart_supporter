from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import UserRepository
from app.utils.errors import NotFoundException


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def list_users(self, skip: int = 0, limit: int = 20) -> list[User]:
        return await self.repo.list(skip=skip, limit=limit)

    async def get_user(self, user_id: int) -> User:
        user = await self.repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def update_user(self, user_id: int, data: dict) -> User:
        user = await self.repo.update(user_id, data)
        if not user:
            raise NotFoundException("User not found")
        return user

    async def delete_user(self, user_id: int) -> None:
        deleted = await self.repo.delete(user_id)
        if not deleted:
            raise NotFoundException("User not found")
