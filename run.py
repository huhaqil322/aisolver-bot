#!/usr/bin/env python3
"""Entry point for local development with polling mode."""

import asyncio
import logging

from app.bot.dispatcher import get_bot, get_dispatcher, start_polling
from app.config.settings import get_settings
from app.utils.logger import setup_logging

settings = get_settings()


async def main() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting AI Solver Bot in polling mode...")
    logger.info(f"Environment: {settings.ENVIRONMENT.value}")
    logger.info(f"Bot token configured: {bool(settings.bot_token)}")

    bot = get_bot()
    bot_info = await bot.get_me()
    logger.info(f"Bot: @{bot_info.username} (ID: {bot_info.id})")

    await start_polling()


if __name__ == "__main__":
    asyncio.run(main())
