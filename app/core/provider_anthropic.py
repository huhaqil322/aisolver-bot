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


class AnthropicProvider(AIProvider):
    provider_name = "anthropic"

    def __init__(self) -> None:
        self.api_key = settings.anthropic_api_key
        self.base_url = "https://api.anthropic.com/v1"
        self.default_model = settings.ANTHROPIC_MODEL
        self.max_tokens = settings.ANTHROPIC_MAX_TOKENS
        self.temperature = settings.ANTHROPIC_TEMPERATURE
        self._client: httpx.AsyncClient | None = None
        self._model_list: list[str] = [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-opus-4-20250514",
        ]

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
        return self._client

    def _convert_messages(self, messages: list[Message]) -> tuple[str, list[dict[str, Any]]]:
        system_msg = ""
        converted = []
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_msg += msg.content + "\n"
            elif msg.role in (MessageRole.USER, MessageRole.ASSISTANT):
                converted.append(
                    {"role": msg.role.value, "content": msg.content}
                )
        return system_msg.strip(), converted

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        start = time.monotonic()
        system_prompt, converted_messages = self._convert_messages(request.messages)

        payload: dict[str, Any] = {
            "model": request.model or self.default_model,
            "messages": converted_messages,
            "max_tokens": request.max_tokens or self.max_tokens,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if request.temperature is not None:
            payload["temperature"] = request.temperature

        response = await self.client.post("/messages", json=payload)
        response.raise_for_status()
        data = response.json()
        elapsed = int((time.monotonic() - start) * 1000)

        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

        usage = data.get("usage", {})
        return CompletionResponse(
            content=content,
            model=data["model"],
            provider=self.provider_name,
            usage={
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
                "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            },
            finish_reason=data.get("stop_reason", "stop"),
            latency_ms=elapsed,
            raw_response=data,
        )

    async def complete_stream(
        self, request: CompletionRequest
    ) -> AsyncGenerator[str, None]:
        system_prompt, converted_messages = self._convert_messages(request.messages)

        payload: dict[str, Any] = {
            "model": request.model or self.default_model,
            "messages": converted_messages,
            "max_tokens": request.max_tokens or self.max_tokens,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(120.0, connect=10.0),
        ) as client:
            async with client.stream("POST", "/messages", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            chunk = json.loads(data_str)
                            if chunk.get("type") == "content_block_delta":
                                delta = chunk.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    text = delta.get("text", "")
                                    if text:
                                        yield text
                        except json.JSONDecodeError:
                            continue

    async def verify_connection(self) -> bool:
        try:
            response = await self.client.post(
                "/messages",
                json={
                    "model": self.default_model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Hi"}],
                },
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_models(self) -> list[str]:
        return self._model_list

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        sonnet_input = 3.00 / 1_000_000
        sonnet_output = 15.00 / 1_000_000
        return (prompt_tokens * sonnet_input) + (completion_tokens * sonnet_output)


if settings.anthropic_api_key:
    ProviderFactory.register("anthropic", AnthropicProvider())
