from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.config.settings import SubscriptionTier

if TYPE_CHECKING:
    from app.models.user import User


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TRIAL = "trial"
    PAUSED = "paused"


class PaymentProvider(str, enum.Enum):
    TELEGRAM = "telegram"
    CRYPTO = "crypto"
    MANUAL = "manual"


class Subscription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier), nullable=False, default=SubscriptionTier.FREE
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIAL
    )
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    payment_provider: Mapped[Optional[PaymentProvider]] = mapped_column(
        Enum(PaymentProvider), nullable=True
    )
    payment_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    daily_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_token_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_used_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    requests_used_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    features_json: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)

    # Relationships
    user: Mapped[User] = relationship(back_populates="subscriptions")


class Payment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "payments"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subscription_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True
    )
    amount: Mapped[float] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    provider: Mapped[PaymentProvider] = mapped_column(
        Enum(PaymentProvider), nullable=False
    )
    provider_payment_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    telegram_charge_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(
        "metadata_json",  # renamed to avoid reserved keyword
        String(2000),
        nullable=True,
    )

    # Relationships
    user: Mapped[User] = relationship(back_populates="payments")
