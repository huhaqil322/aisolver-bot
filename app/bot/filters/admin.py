from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from app.config.settings import get_settings

settings = get_settings()


class AdminFilter(Filter):
    key = "is_admin"

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user = event.from_user
        if not user:
            return False
        return user.id in settings.TELEGRAM_ADMIN_IDS
