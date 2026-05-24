from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class RequestType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    VOICE = "voice"
    OCR = "ocr"


class RequestLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "request_logs"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    conversation_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True
    )
    request_type: Mapped[RequestType] = mapped_column(
        Enum(RequestType), nullable=False
    )
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus), nullable=False, default=RequestStatus.PENDING
    )
    subject: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    request_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped[User] = relationship(back_populates="request_logs")
