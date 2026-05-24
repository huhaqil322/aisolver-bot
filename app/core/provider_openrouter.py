from __future__ import annotations

import json
import time
from typing import Any, AsyncGenerator, Optional

import httpx

from app.config.settings import get_settings
from app.core.ai_provider import (
    AIProvider,
    CompletionRequest,
    CompletionResponse,
    Message,
    MessageRole,
    ProviderFactory,
)

settings = get_settings()


class OpenRouterProvider(AIProvider):
    provider_name = "openrouter"

    def __init__(self) -> None:
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.OPENROUTER_BASE_URL
        self.default_model = settings.OPENROUTER_MODEL
        self.max_tokens = settings.OPENROUTER_MAX_TOKENS
        self.temperature = settings.OPENROUTER_TEMPERATURE
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://t.me/aisolverbot",
                    "X-Title": "AISolverBot",
                },
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
        return self._client

    def _convert_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        converted = []
        for msg in messages:
            entry: dict[str, Any] = {"role": msg.role.value, "content": msg.content}
            if msg.name:
                entry["name"] = msg.name
            converted.append(entry)
        return converted

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        start = time.monotonic()
        payload: dict[str, Any] = {
            "model": request.model or self.default_model,
            "messages": self._convert_messages(request.messages),
            "max_tokens": request.max_tokens or self.max_tokens,
            "temperature": request.temperature or self.temperature,
        }
        if request.tools:
            payload["tools"] = request.tools

        response = await self.client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        elapsed = int((time.monotonic() - start) * 1000)

        choice = data["choices"][0]
        usage = data.get("usage", {})
        return CompletionResponse(
            content=choice["message"]["content"] or "",
            model=data["model"],
            provider=self.provider_name,
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
            finish_reason=choice.get("finish_reason", "stop"),
            latency_ms=elapsed,
            raw_response=data,
        )

    async def complete_stream(
        self, request: CompletionRequest
    ) -> AsyncGenerator[str, None]:
        payload: dict[str, Any] = {
            "model": request.model or self.default_model,
            "messages": self._convert_messages(request.messages),
            "max_tokens": request.max_tokens or self.max_tokens,
            "temperature": request.temperature or self.temperature,
            "stream": True,
        }

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(120.0, connect=10.0),
        ) as client:
            async with client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

    async def verify_connection(self) -> bool:
        try:
            response = await self.client.get("/models", params={"limit": 1})
            return response.status_code == 200
        except Exception:
            return False

    def get_models(self) -> list[str]:
        return [self.default_model, "openai/gpt-4o-mini", "anthropic/claude-sonnet-4"]

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        gpt4o_input = 2.50 / 1_000_000
        gpt4o_output = 10.00 / 1_000_000
        return (prompt_tokens * gpt4o_input) + (completion_tokens * gpt4o_output)


if settings.openrouter_api_key:
    ProviderFactory.register("openrouter", OpenRouterProvider())
