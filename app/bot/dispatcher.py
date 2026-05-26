from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from app.bot.handlers import admin, image, problem, profile, start
from app.bot.handlers.history import router as history_router
from app.bot.middlewares.throttling import ThrottlingMiddleware
from app.config.settings import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

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


async def create_storage() -> MemoryStorage | RedisStorage:
    url = settings.redis_url_str
    try:
        from redis.asyncio import Redis

        client = Redis.from_url(url, socket_connect_timeout=2)
        await client.ping()
        storage = RedisStorage(client)
        logger.info("Using Redis storage: %s", url)
        return storage
    except Exception:
        logger.warning("Redis unavailable (%s), falling back to MemoryStorage", url)
        return MemoryStorage()


async def get_dispatcher() -> Dispatcher:
    global _dp
    if _dp is None:
        storage = await create_storage()

        _dp = Dispatcher(storage=storage)

        _dp.message.middleware(ThrottlingMiddleware())
        _dp.callback_query.middleware(ThrottlingMiddleware())

        _dp.include_routers(
            start.router,
            problem.router,
            image.router,
            profile.router,
            admin.router,
            history_router,
        )

    return _dp


async def setup_bot() -> None:
    bot = get_bot()
    dp = await get_dispatcher()

    if settings.TELEGRAM_WEBHOOK_URL:
        base_url = settings.TELEGRAM_WEBHOOK_URL.rstrip("/")
        webhook_url = f"{base_url}{settings.API_PREFIX}/webhook"
        logger.info("Setting webhook: %s", webhook_url)
        result = await bot.set_webhook(
            url=webhook_url,
            secret_token=settings.TELEGRAM_WEBHOOK_SECRET,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True,
        )
        logger.info("Webhook set result: %s", result)
    else:
        logger.warning("TELEGRAM_WEBHOOK_URL not set, deleting webhook")
        await bot.delete_webhook(drop_pending_updates=True)


async def start_polling() -> None:
    bot = get_bot()
    dp = await get_dispatcher()
    await dp.start_polling(bot)
