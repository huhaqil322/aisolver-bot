from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Optional, Protocol


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[list[dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class CompletionRequest:
    messages: list[Message]
    model: str
    max_tokens: int = 4096
    temperature: float = 0.3
    top_p: float = 0.95
    stop: Optional[list[str]] = None
    stream: bool = False
    tools: Optional[list[dict[str, Any]]] = None
    tool_choice: Optional[str] = None
    response_format: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResponse:
    content: str
    model: str
    provider: str
    usage: dict[str, int]
    finish_reason: str
    latency_ms: int
    raw_response: Optional[Any] = None


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0


class AIProvider(ABC):
    provider_name: str = ""

    @abstractmethod
    async def complete(
        self, request: CompletionRequest
    ) -> CompletionResponse:
        ...

    @abstractmethod
    async def complete_stream(
        self, request: CompletionRequest
    ) -> AsyncGenerator[str, None]:
        ...

    @abstractmethod
    async def verify_connection(self) -> bool:
        ...

    @abstractmethod
    def get_models(self) -> list[str]:
        ...

    @abstractmethod
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        ...


class ProviderFactory:
    _providers: dict[str, AIProvider] = {}

    @classmethod
    def register(cls, name: str, provider: AIProvider) -> None:
        cls._providers[name] = provider

    @classmethod
    def get(cls, name: str) -> Optional[AIProvider]:
        return cls._providers.get(name)

    @classmethod
    def get_available(cls) -> dict[str, AIProvider]:
        return dict(cls._providers)

    @classmethod
    def get_all_names(cls) -> list[str]:
        return list(cls._providers.keys())
