from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from fastapi import APIRouter, FastAPI, Header, HTTPException, Request, Response, status

from app.bot.dispatcher import get_bot, get_dispatcher
from app.config.settings import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)
router = APIRouter(prefix=settings.API_PREFIX)


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None),
) -> Response:
    if settings.TELEGRAM_WEBHOOK_SECRET:
        if x_telegram_bot_api_secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
            logger.warning("Invalid secret token")
            raise HTTPException(status_code=403, detail="Invalid secret token")

    try:
        body = await request.json()
        bot = get_bot()
        dp = get_dispatcher()
        update = Update.model_validate(body, context={"bot": bot})
        logger.debug("Received update: %s", update.update_id)
        await dp.feed_update(bot=bot, update=update)
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Webhook error: %s", e, exc_info=True)
        return Response(status_code=status.HTTP_200_OK)


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT.value,
    }


@router.get("/metrics")
async def metrics() -> dict:
    return {
        "requests_total": 0,
        "active_users": 0,
        "ai_cost_total": 0.0,
        "uptime_seconds": 0,
    }
