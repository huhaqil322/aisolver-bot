from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.conversation import Conversation
    from app.models.payment import Payment
    from app.models.request_log import RequestLog


class UserLanguage(str, enum.Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    CHINESE = "zh"
    ARABIC = "ar"
    PORTUGUESE = "pt"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BANNED = "banned"
    LIMITED = "limited"
    INACTIVE = "inactive"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    language: Mapped[UserLanguage] = mapped_column(
        Enum(UserLanguage), default=UserLanguage.ENGLISH, nullable=False
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False
    )

    # Stats
    total_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens_used: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    daily_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    monthly_tokens_used: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    monthly_reset_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Referral
    referral_code: Mapped[str] = mapped_column(
        String(32), unique=True, nullable=False, index=True
    )
    referred_by: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    referral_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Preferences
    preferred_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    preferred_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    explanation_level: Mapped[str] = mapped_column(
        String(20), default="intermediate", nullable=False
    )
    streaming_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Metadata
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    feedback_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # AI usage metadata
    ai_provider_usage: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )  # JSON blob

    # Relationships
    conversations: Mapped[List[Conversation]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    payments: Mapped[List[Payment]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    request_logs: Mapped[List[RequestLog]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
