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


class GeminiProvider(AIProvider):
    provider_name = "gemini"

    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key
        self.default_model = settings.GEMINI_MODEL
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        self.temperature = settings.GEMINI_TEMPERATURE
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self._client: httpx.AsyncClient | None = None
        self._model_list: list[str] = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
        return self._client

    def _convert_messages(self, messages: list[Message]) -> tuple[Optional[str], list[dict[str, Any]]]:
        system_msg = None
        contents = []
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_msg = msg.content
            elif msg.role == MessageRole.USER:
                contents.append({"role": "user", "parts": [{"text": msg.content}]})
            elif msg.role == MessageRole.ASSISTANT:
                contents.append({"role": "model", "parts": [{"text": msg.content}]})
        return system_msg, contents

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        start = time.monotonic()
        model = request.model or self.default_model
        system_prompt, contents = self._convert_messages(request.messages)

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": request.max_tokens or self.max_tokens,
            },
        }
        if request.temperature is not None:
            payload["generationConfig"]["temperature"] = request.temperature
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        url = f"/models/{model}:generateContent?key={self.api_key}"
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        elapsed = int((time.monotonic() - start) * 1000)

        candidate = data.get("candidates", [{}])[0]
        content_parts = candidate.get("content", {}).get("parts", [])
        full_text = "".join(p.get("text", "") for p in content_parts)
        finish_reason = candidate.get("finishReason", "stop")

        usage = data.get("usageMetadata", {})
        return CompletionResponse(
            content=full_text,
            model=model,
            provider=self.provider_name,
            usage={
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("totalTokenCount", 0),
            },
            finish_reason=finish_reason,
            latency_ms=elapsed,
            raw_response=data,
        )

    async def complete_stream(
        self, request: CompletionRequest
    ) -> AsyncGenerator[str, None]:
        model = request.model or self.default_model
        system_prompt, contents = self._convert_messages(request.messages)

        payload: dict[str, Any] = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": request.max_tokens or self.max_tokens,
            },
        }
        if request.temperature is not None:
            payload["generationConfig"]["temperature"] = request.temperature
        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        url = f"/models/{model}:streamGenerateContent?alt=sse&key={self.api_key}"
        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Content-Type": "application/json"},
            timeout=httpx.Timeout(120.0, connect=10.0),
        ) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            chunk = json.loads(data_str)
                            candidate = chunk.get("candidates", [{}])[0]
                            parts = candidate.get("content", {}).get("parts", [])
                            for p in parts:
                                text = p.get("text", "")
                                if text:
                                    yield text
                        except (json.JSONDecodeError, IndexError, KeyError):
                            continue

    async def verify_connection(self) -> bool:
        try:
            url = f"/models?key={self.api_key}"
            response = await self.client.get(url)
            return response.status_code == 200
        except Exception:
            return False

    def get_models(self) -> list[str]:
        return self._model_list

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        gemini_input = 0.10 / 1_000_000
        gemini_output = 0.40 / 1_000_000
        return (prompt_tokens * gemini_input) + (completion_tokens * gemini_output)


if settings.gemini_api_key:
    ProviderFactory.register("gemini", GeminiProvider())
