from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import Field, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    GEMINI = "gemini"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    APP_NAME: str = "AISolverBot"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    LOG_LEVEL: LogLevel = LogLevel.INFO
    SECRET_KEY: SecretStr = Field(default="dev-secret-key-change-in-production", alias="SECRET_KEY")
    API_PREFIX: str = "/api/v1"

    # Telegram
    TELEGRAM_BOT_TOKEN: SecretStr = Field(default="placeholder:set-telegram-bot-token", alias="TELEGRAM_BOT_TOKEN")
    TELEGRAM_WEBHOOK_URL: str | None = None
    TELEGRAM_WEBHOOK_SECRET: str | None = None
    TELEGRAM_ADMIN_IDS: list[int] = Field(default_factory=list)

    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/aisolver",
        alias="DATABASE_URL",
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: RedisDsn = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL",
    )
    REDIS_POOL_SIZE: int = 20

    # AI Providers - OpenAI
    OPENAI_API_KEY: SecretStr | None = None
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.3

    # AI Providers - Anthropic
    ANTHROPIC_API_KEY: SecretStr | None = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_MAX_TOKENS: int = 4096
    ANTHROPIC_TEMPERATURE: float = 0.3

    # AI Providers - OpenRouter
    OPENROUTER_API_KEY: SecretStr | None = None
    OPENROUTER_MODEL: str = "openai/gpt-4o"
    OPENROUTER_MAX_TOKENS: int = 4096
    OPENROUTER_TEMPERATURE: float = 0.3
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # AI Providers - Gemini
    GEMINI_API_KEY: SecretStr | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_MAX_TOKENS: int = 4096
    GEMINI_TEMPERATURE: float = 0.3

    # Default AI Provider
    DEFAULT_AI_PROVIDER: AIProvider = AIProvider.OPENROUTER
    AI_FALLBACK_ENABLED: bool = True
    AI_STREAMING_ENABLED: bool = True

    # OCR
    OCR_ENABLED: bool = True
    TESSERACT_CMD: str = "/usr/bin/tesseract"
    MATHPIX_API_KEY: SecretStr | None = None
    MATHPIX_APP_ID: str | None = None
    MAX_IMAGE_SIZE_MB: int = 10
    SUPPORTED_IMAGE_FORMATS: list[str] = Field(
        default_factory=lambda: ["jpg", "jpeg", "png", "bmp", "tiff", "webp"]
    )

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_BURST: int = 20

    # User Limits
    DAILY_LIMIT: int = 20
    TOKENS_PER_MONTH: int = 100000

    # Referral
    REFERRAL_ENABLED: bool = True
    REFERRAL_BONUS_DAYS: int = 3
    REFERRAL_BONUS_TOKENS: int = 10000

    # Workers
    WORKER_CONCURRENCY: int = 5
    WORKER_TIMEOUT_SECONDS: int = 300
    TASK_QUEUE_MAX_SIZE: int = 1000

    # Redis Queue
    REDIS_QUEUE_OCR: str = "queue:ocr"
    REDIS_QUEUE_AI: str = "queue:ai"
    REDIS_QUEUE_ANALYTICS: str = "queue:analytics"
    REDIS_QUEUE_NOTIFICATIONS: str = "queue:notifications"

    # Admin
    ADMIN_BROADCAST_BATCH_SIZE: int = 100
    ADMIN_RATE_LIMIT: int = 30

    # Security
    MAX_MESSAGE_LENGTH: int = 4096
    MAX_PROMPT_LENGTH: int = 8000
    ENABLE_CONTENT_FILTERING: bool = True
    API_KEY_HEADER: str = "X-API-Key"

    # Monitoring
    SENTRY_DSN: str | None = None
    OPENTELEMETRY_ENABLED: bool = False
    ENABLE_METRICS: bool = True

    # Paths
    BASE_DIR: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent.parent)
    UPLOAD_DIR: Path = Path("/tmp/aisolver/uploads")
    LOG_DIR: Path = Path("/var/log/aisolver")
    DATA_DIR: Path = Path("/data/aisolver")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT

    @property
    def bot_token(self) -> str:
        return self.TELEGRAM_BOT_TOKEN.get_secret_value()

    @property
    def database_url_str(self) -> str:
        return str(self.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://")

    @property
    def redis_url_str(self) -> str:
        return str(self.REDIS_URL)

    @property
    def openai_api_key(self) -> str | None:
        return self.OPENAI_API_KEY.get_secret_value() if self.OPENAI_API_KEY else None

    @property
    def anthropic_api_key(self) -> str | None:
        return self.ANTHROPIC_API_KEY.get_secret_value() if self.ANTHROPIC_API_KEY else None

    @property
    def openrouter_api_key(self) -> str | None:
        return self.OPENROUTER_API_KEY.get_secret_value() if self.OPENROUTER_API_KEY else None

    @property
    def gemini_api_key(self) -> str | None:
        return self.GEMINI_API_KEY.get_secret_value() if self.GEMINI_API_KEY else None

    @property
    def mathpix_api_key(self) -> str | None:
        return self.MATHPIX_API_KEY.get_secret_value() if self.MATHPIX_API_KEY else None

    def get_available_providers(self) -> list[AIProvider]:
        providers = []
        if self.openai_api_key:
            providers.append(AIProvider.OPENAI)
        if self.anthropic_api_key:
            providers.append(AIProvider.ANTHROPIC)
        if self.openrouter_api_key:
            providers.append(AIProvider.OPENROUTER)
        if self.gemini_api_key:
            providers.append(AIProvider.GEMINI)
        return providers


@lru_cache()
def get_settings() -> Settings:
    return Settings()
