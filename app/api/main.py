from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.webhook import router as webhook_router
from app.bot.dispatcher import setup_bot
from app.config.settings import get_settings
from app.utils.logger import setup_logging, get_logger

logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger.info("Starting %s v%s (%s)", settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT.value)
    logger.info("WEBHOOK_URL configured: %s", bool(settings.TELEGRAM_WEBHOOK_URL))
    logger.info("BOT_TOKEN configured: %s", bool(settings.bot_token) and settings.bot_token != "placeholder:set-telegram-bot-token")
    try:
        await setup_bot()
    except Exception as e:
        logger.warning(f"Bot setup failed (non-fatal): {e}")
    yield
    bot = getattr(app.state, "bot", None)
    if bot:
        await bot.session.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url=f"{settings.API_PREFIX}/docs" if settings.is_development else None,
        redoc_url=f"{settings.API_PREFIX}/redoc" if settings.is_development else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )

    app.include_router(webhook_router)

    return app


app = create_app()
