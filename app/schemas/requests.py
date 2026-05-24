from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SolveRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    subject: Optional[str] = None
    language: str = "en"
    explanation_level: str = "intermediate"
    provider: Optional[str] = None
    model: Optional[str] = None
    stream: bool = False
    conversation_id: Optional[str] = None


class SolveResponse(BaseModel):
    answer: str
    subject: str
    confidence: float
    tokens_used: dict[str, int]
    provider: str
    model: str
    processing_time_ms: int


class OCRRequest(BaseModel):
    image_url: Optional[str] = None
    language: str = "eng+rus"


class OCRResponse(BaseModel):
    text: str
    confidence: float
    is_handwritten: bool
    formulas: list[str]


class AdminBroadcastRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    parse_mode: str = "Markdown"
    user_ids: Optional[list[int]] = None


class UserUpdateRequest(BaseModel):
    language: Optional[str] = None
    explanation_level: Optional[str] = None
    preferred_provider: Optional[str] = None
    preferred_model: Optional[str] = None
    streaming_enabled: Optional[bool] = None


class FeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class PaginationParams(BaseModel):
    page: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
