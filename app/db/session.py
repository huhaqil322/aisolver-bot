from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    AsyncSessionTransaction,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, QueuePool

from app.config.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url_str,
    poolclass=QueuePool if not settings.DEBUG else NullPool,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_use_lifo=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_connection() -> AsyncGenerator[AsyncConnection, Any]:
    async with engine.connect() as conn:
        yield conn


async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_transaction_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._transaction: AsyncSessionTransaction | None = None

    async def __aenter__(self) -> UnitOfWork:
        self._transaction = await self.session.begin()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._transaction:
            if args[0] is None:
                await self._transaction.commit()
            else:
                await self._transaction.rollback()
            self._transaction = None

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def flush(self) -> None:
        await self.session.flush()
