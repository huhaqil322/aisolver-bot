from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.config.settings import get_settings

settings = get_settings()


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(
        self,
        rate_limit: int = 10,
        window_seconds: int = 60,
        burst_limit: int = 20,
    ) -> None:
        self.rate_limit = rate_limit
        self.window_seconds = window_seconds
        self.burst_limit = burst_limit
        self.user_requests: Dict[int, list[float]] = defaultdict(list)
        self.cache: Dict[str, Any] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Optional[Any]:
        if not settings.RATE_LIMIT_ENABLED:
            return await handler(event, data)

        user = None
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user

        if user and user.id in settings.TELEGRAM_ADMIN_IDS:
            return await handler(event, data)

        if user:
            user_id = user.id
            now = time.time()
            window_start = now - self.window_seconds

            self.user_requests[user_id] = [
                t for t in self.user_requests[user_id] if t > window_start
            ]

            if len(self.user_requests[user_id]) >= self.rate_limit:
                if isinstance(event, Message):
                    await event.answer(
                        f"⏱ Rate limit exceeded. "
                        f"Max {self.rate_limit} requests per {self.window_seconds}s. "
                        f"Please wait and try again."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        f"⏱ Please slow down!", show_alert=True
                    )
                return None

            self.user_requests[user_id].append(now)

        return await handler(event, data)
