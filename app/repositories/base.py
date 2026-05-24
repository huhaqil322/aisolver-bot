from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: type[ModelType]) -> None:
        self._session = session
        self._model = model

    async def create(self, **kwargs: Any) -> ModelType:
        instance = self._model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        return instance

    async def get(self, id: UUID) -> Optional[ModelType]:
        stmt = select(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by(self, **kwargs: Any) -> Optional[ModelType]:
        stmt = select(self._model).filter_by(**kwargs)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        **filters: Any,
    ) -> list[ModelType]:
        stmt = select(self._model).filter_by(**filters).offset(skip).limit(limit)
        if order_by:
            column = getattr(self._model, order_by.lstrip("-"), None)
            if column is not None:
                stmt = stmt.order_by(column.desc() if order_by.startswith("-") else column)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, id: UUID, **kwargs: Any) -> Optional[ModelType]:
        stmt = (
            update(self._model)
            .where(self._model.id == id)
            .values(**kwargs)
            .returning(self._model)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one_or_none()

    async def delete(self, id: UUID) -> bool:
        stmt = delete(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0

    async def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self._model).filter_by(**filters)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def exists(self, **kwargs: Any) -> bool:
        stmt = select(self._model).filter_by(**kwargs).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def bulk_create(self, instances: list[ModelType]) -> list[ModelType]:
        self._session.add_all(instances)
        await self._session.flush()
        return instances

    async def refresh(self, instance: ModelType) -> None:
        await self._session.refresh(instance)
