from abc import ABC
from typing import Any, Generic, TypeVar

from sqlalchemy import select, update as sa_update, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")


class BaseRepository(ABC, Generic[ModelT]):
    model_class: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, model: ModelT) -> ModelT:
        self.db.add(model)
        await self.db.flush()
        await self.db.refresh(model)
        return model

    async def get(self, id: int) -> ModelT | None:
        result = await self.db.execute(
            select(self.model_class).where(self.model_class.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 20) -> list[ModelT]:
        result = await self.db.execute(
            select(self.model_class).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, id: int, data: dict[str, Any]) -> ModelT | None:
        result = await self.db.execute(
            sa_update(self.model_class)
            .where(self.model_class.id == id)  # type: ignore[attr-defined]
            .values(**data)
            .returning(self.model_class)
        )
        await self.db.flush()
        return result.scalar_one_or_none()

    async def delete(self, id: int) -> bool:
        result = await self.db.execute(
            sa_delete(self.model_class).where(self.model_class.id == id)  # type: ignore[attr-defined]
        )
        await self.db.flush()
        return bool(result.rowcount)  # type: ignore[attr-defined]
