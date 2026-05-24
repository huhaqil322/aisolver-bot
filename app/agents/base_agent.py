from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from app.core.ai_provider import (
    AIProvider,
    CompletionRequest,
    CompletionResponse,
    Message,
    MessageRole,
    ProviderFactory,
    TokenUsage,
)
from app.config.settings import get_settings

settings = get_settings()


class AgentType(str, Enum):
    MATH = "math"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    CODE = "code"
    OCR = "ocr"
    VALIDATOR = "validator"
    EXPLANATION = "explanation"
    ORCHESTRATOR = "orchestrator"


@dataclass
class AgentContext:
    user_id: str
    conversation_id: Optional[str] = None
    language: str = "en"
    explanation_level: str = "intermediate"
    provider: Optional[str] = None
    model: Optional[str] = None
    subject: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    content: str
    agent_type: AgentType
    confidence: float = 1.0
    tokens_used: TokenUsage = field(default_factory=TokenUsage)
    provider: Optional[str] = None
    model: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    requires_verification: bool = True


class BaseAgent(ABC):
    def __init__(
        self,
        agent_type: AgentType,
        system_prompt: str,
        provider_name: Optional[str] = None,
    ) -> None:
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self._provider_name = provider_name or settings.DEFAULT_AI_PROVIDER.value

    @property
    def provider(self) -> AIProvider:
        provider = ProviderFactory.get(self._provider_name)
        if provider is None:
            available = ProviderFactory.get_all_names()
            if available:
                provider = ProviderFactory.get(available[0])
            if provider is None:
                raise RuntimeError(f"No AI providers available. Configured: {available}")
            self._provider_name = available[0]
        return provider

    def build_messages(
        self, prompt: str, context: AgentContext, **kwargs: Any
    ) -> list[Message]:
        messages: list[Message] = [
            Message(role=MessageRole.SYSTEM, content=self.system_prompt),
        ]

        if context.metadata.get("history"):
            for hist_msg in context.metadata["history"][-10:]:
                messages.append(
                    Message(
                        role=MessageRole.USER
                        if hist_msg.get("role") == "user"
                        else MessageRole.ASSISTANT,
                        content=hist_msg.get("content", ""),
                    )
                )

        messages.append(Message(role=MessageRole.USER, content=prompt))
        return messages

    async def process(
        self, prompt: str, context: AgentContext, **kwargs: Any
    ) -> AgentResult:
        try:
            messages = self.build_messages(prompt, context, **kwargs)
            request = CompletionRequest(
                messages=messages,
                model=context.model or settings.OPENAI_MODEL,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
                stream=False,
            )
            response = await self.provider.complete(request)
            return AgentResult(
                content=response.content,
                agent_type=self.agent_type,
                tokens_used=TokenUsage(
                    prompt_tokens=response.usage.get("prompt_tokens", 0),
                    completion_tokens=response.usage.get("completion_tokens", 0),
                    total_tokens=response.usage.get("total_tokens", 0),
                    cost=self.provider.calculate_cost(
                        response.usage.get("prompt_tokens", 0),
                        response.usage.get("completion_tokens", 0),
                    ),
                ),
                provider=response.provider,
                model=response.model,
            )
        except Exception as e:
            return AgentResult(
                content="",
                agent_type=self.agent_type,
                error=str(e),
                confidence=0.0,
            )

    async def process_stream(
        self, prompt: str, context: AgentContext, **kwargs: Any
    ):
        messages = self.build_messages(prompt, context, **kwargs)
        request = CompletionRequest(
            messages=messages,
            model=context.model or settings.OPENAI_MODEL,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            temperature=settings.OPENAI_TEMPERATURE,
            stream=True,
        )
        async for chunk in self.provider.complete_stream(request):
            yield chunk
