from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserStatus
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        return await self.get_by(telegram_id=telegram_id)

    async def get_by_referral_code(self, code: str) -> Optional[User]:
        return await self.get_by(referral_code=code)

    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language_code: str = "en",
    ) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            update_data: dict = {"last_activity_at": datetime.now(timezone.utc)}
            if username:
                update_data["username"] = username
            if first_name:
                update_data["first_name"] = first_name
            if last_name:
                update_data["last_name"] = last_name
            for key, value in update_data.items():
                setattr(user, key, value)
            await self._session.flush()
            return user

        import secrets
        import string

        referral_code = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(8)
        )
        user = await self.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
            referral_code=referral_code,
            last_activity_at=datetime.now(timezone.utc),
        )
        return user

    async def increment_requests(self, user_id: UUID, tokens: int = 0) -> None:
        user = await self.get(user_id)
        if user:
            user.total_requests += 1
            user.daily_requests += 1
            if tokens:
                user.total_tokens_used += tokens
                user.monthly_tokens_used += tokens
            await self._session.flush()

    async def get_active_users_count(
        self, since: Optional[datetime] = None
    ) -> int:
        stmt = select(func.count(self._model.id)).where(
            self._model.status == UserStatus.ACTIVE
        )
        if since:
            stmt = stmt.where(self._model.last_activity_at >= since)
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_admins(self) -> list[User]:
        stmt = (
            select(self._model)
            .where(self._model.is_admin == True)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def search_users(
        self, query: str, skip: int = 0, limit: int = 50
    ) -> list[User]:
        stmt = (
            select(self._model)
            .where(
                or_(
                    self._model.username.ilike(f"%{query}%"),
                    self._model.first_name.ilike(f"%{query}%"),
                    self._model.last_name.ilike(f"%{query}%"),
                    self._model.telegram_id.cast(str).ilike(f"%{query}%"),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_top_users_by_requests(
        self, limit: int = 10
    ) -> list[User]:
        stmt = (
            select(self._model)
            .where(self._model.status == UserStatus.ACTIVE)
            .order_by(self._model.total_requests.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
