import pytest
from app.config.settings import Settings, Environment


def test_settings_defaults():
    settings = Settings(
        SECRET_KEY="test-secret",
        TELEGRAM_BOT_TOKEN="test:token",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/test",
        REDIS_URL="redis://localhost:6379/0",
    )
    assert settings.APP_NAME == "AISolverBot"
    assert settings.ENVIRONMENT == Environment.DEVELOPMENT
    assert settings.FREE_DAILY_LIMIT == 20
    assert settings.bot_token == "test:token"
