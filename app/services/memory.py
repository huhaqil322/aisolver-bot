from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from aiogram.types import User as TelegramUser

from app.config.settings import get_settings

settings = get_settings()

_user_cache: dict[int, dict[str, Any]] = {}


async def get_user_context(telegram_user: TelegramUser) -> dict[str, Any]:
    user_id = telegram_user.id
    if user_id in _user_cache:
        context = _user_cache[user_id]
        context["last_activity"] = datetime.now(timezone.utc).isoformat()
        return context

    is_admin = user_id in settings.TELEGRAM_ADMIN_IDS
    context: dict[str, Any] = {
        "telegram_id": user_id,
        "username": telegram_user.username,
        "first_name": telegram_user.first_name,
        "language": telegram_user.language_code or "en",
        "is_admin": is_admin,
        "is_premium": False,
        "total_requests": 0,
        "daily_requests": 0,
        "monthly_tokens": 0,
        "total_tokens": 0,
        "daily_limit": settings.FREE_DAILY_LIMIT,
        "monthly_limit": settings.FREE_TOKENS_PER_MONTH,
        "referral_count": 0,
        "conversations_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_activity": datetime.now(timezone.utc).isoformat(),
    }

    _user_cache[user_id] = context
    return context


async def update_user_context(user_id: int, **kwargs: Any) -> None:
    if user_id in _user_cache:
        _user_cache[user_id].update(kwargs)


async def get_conversation_history(
    user_id: int, limit: int = 10
) -> list[dict[str, str]]:
    _history: dict[int, list[dict[str, str]]] = {}
    return _history.get(user_id, [])[-limit:]


async def add_to_history(user_id: int, role: str, content: str) -> None:
    _history: dict[int, list[dict[str, str]]] = {}
    if user_id not in _history:
        _history[user_id] = []
    _history[user_id].append({
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    if len(_history[user_id]) > 100:
        _history[user_id] = _history[user_id][-100:]


class CacheService:
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}

    async def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._store[key] = value

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def exists(self, key: str) -> bool:
        return key in self._store

    async def clear(self) -> None:
        self._store.clear()
