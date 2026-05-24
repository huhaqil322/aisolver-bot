from __future__ import annotations

import logging
import sys
from typing import Optional

from app.config.settings import get_settings

settings = get_settings()


def setup_logging() -> None:
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.value, logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    if settings.is_production:
        try:
            from logging.handlers import RotatingFileHandler

            settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                settings.LOG_DIR / "app.log",
                maxBytes=100 * 1024 * 1024,
                backupCount=10,
            )
            file_handler.setFormatter(
                logging.Formatter(log_format, datefmt=date_format)
            )
            logging.getLogger().addHandler(file_handler)
        except Exception:
            pass

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.WARNING if not settings.DATABASE_ECHO else logging.INFO
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
