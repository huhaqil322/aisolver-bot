from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from app.bot.handlers import admin, image, payments, problem, profile, start
from app.bot.handlers.history import router as history_router
from app.bot.middlewares.throttling import ThrottlingMiddleware
from app.config.settings import get_settings

settings = get_settings()

_bot: Bot | None = None
_dp: Dispatcher | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
        )
    return _bot


def get_dispatcher() -> Dispatcher:
    global _dp
    if _dp is None:
        storage: MemoryStorage | RedisStorage
        try:
            from redis.asyncio import Redis

            redis_client = Redis.from_url(settings.redis_url_str)
            storage = RedisStorage(redis_client)
        except Exception:
            storage = MemoryStorage()

        _dp = Dispatcher(storage=storage)

        _dp.message.middleware(ThrottlingMiddleware())
        _dp.callback_query.middleware(ThrottlingMiddleware())

        _dp.include_routers(
            start.router,
            problem.router,
            image.router,
            profile.router,
            payments.router,
            admin.router,
            history_router,
        )

    return _dp


async def setup_bot() -> None:
    bot = get_bot()
    dp = get_dispatcher()

    if settings.TELEGRAM_WEBHOOK_URL:
        webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}{settings.API_PREFIX}/webhook"
        await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.TELEGRAM_WEBHOOK_SECRET,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
    else:
        await bot.delete_webhook(drop_pending_updates=True)


async def start_polling() -> None:
    bot = get_bot()
    dp = get_dispatcher()
    await dp.start_polling(bot)
