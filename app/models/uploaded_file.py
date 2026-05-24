from __future__ import annotations

import enum
from typing import Optional

from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin


class FileType(str, enum.Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    VOICE = "voice"
    VIDEO = "video"
    OTHER = "other"


class UploadedFile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "uploaded_files"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_type: Mapped[FileType] = mapped_column(
        Enum(FileType), nullable=False
    )
    telegram_file_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    telegram_file_unique_id: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    original_filename: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    local_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
