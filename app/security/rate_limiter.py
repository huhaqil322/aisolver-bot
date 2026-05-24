from __future__ import annotations

import time
from collections import defaultdict
from typing import Optional


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds

        self._requests[key] = [
            t for t in self._requests[key] if t > window_start
        ]

        if len(self._requests[key]) >= self.max_requests:
            return False

        self._requests[key].append(now)
        return True

    def get_remaining(self, key: str) -> int:
        now = time.time()
        window_start = now - self.window_seconds
        active = sum(1 for t in self._requests[key] if t > window_start)
        return max(0, self.max_requests - active)

    def get_reset_time(self, key: str) -> float:
        if not self._requests[key]:
            return 0
        return self._requests[key][0] + self.window_seconds - time.time()

    def reset(self, key: str) -> None:
        self._requests[key] = []


class TokenBucketRateLimiter:
    def __init__(self, capacity: int = 20, refill_rate: float = 1.0) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: dict[str, dict] = {}

    def check(self, key: str, tokens: int = 1) -> bool:
        now = time.time()
        if key not in self._buckets:
            self._buckets[key] = {
                "tokens": self.capacity,
                "last_refill": now,
            }

        bucket = self._buckets[key]
        elapsed = now - bucket["last_refill"]
        bucket["tokens"] = min(
            self.capacity,
            bucket["tokens"] + elapsed * self.refill_rate,
        )
        bucket["last_refill"] = now

        if bucket["tokens"] >= tokens:
            bucket["tokens"] -= tokens
            return True

        return False


def validate_telegram_id(telegram_id: int) -> bool:
    return 100_000_000 <= telegram_id <= 999_999_999_999


def sanitize_input(text: str, max_length: int = 8000) -> str:
    import re

    sanitized = text.strip()[:max_length]
    sanitized = re.sub(r"<[^>]*>", "", sanitized)
    return sanitized


def validate_file_size(size_bytes: int, max_mb: int = 10) -> bool:
    return size_bytes <= max_mb * 1024 * 1024
