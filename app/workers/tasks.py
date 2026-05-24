from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class TaskPriority(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class TaskType(Enum):
    OCR = "ocr"
    AI_COMPLETION = "ai_completion"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    SUBSCRIPTION_CHECK = "subscription_check"
    CLEANUP = "cleanup"
    BROADCAST = "broadcast"


@dataclass
class Task:
    id: str
    type: TaskType
    payload: dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: float = field(default_factory=time.time)
    max_retries: int = 3
    retry_count: int = 0
    timeout_seconds: int = 300


class TaskQueue:
    def __init__(self, max_size: int = 1000) -> None:
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_size)
        self._handlers: dict[TaskType, Callable] = {}

    def register_handler(self, task_type: TaskType, handler: Callable) -> None:
        self._handlers[task_type] = handler

    async def enqueue(self, task: Task) -> None:
        await self._queue.put((task.priority.value, time.time(), task))

    async def dequeue(self) -> Optional[Task]:
        try:
            _, _, task = await self._queue.get()
            return task
        except asyncio.QueueEmpty:
            return None

    async def process_next(self) -> bool:
        task = await self.dequeue()
        if task is None:
            return False

        handler = self._handlers.get(task.type)
        if handler is None:
            return False

        try:
            await asyncio.wait_for(
                handler(task), timeout=task.timeout_seconds
            )
            return True
        except Exception:
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                await self.enqueue(task)
            return False


_global_queue: TaskQueue | None = None


def get_task_queue() -> TaskQueue:
    global _global_queue
    if _global_queue is None:
        _global_queue = TaskQueue()
    return _global_queue


async def ocr_task_handler(task: Task) -> None:
    image_path = task.payload.get("image_path")
    file_id = task.payload.get("file_id")
    user_id = task.payload.get("user_id")

    from app.ocr.pipeline import OCRPipeline

    ocr = OCRPipeline()
    from pathlib import Path

    result = await ocr.process_from_path(Path(image_path))
    task.payload["result"] = {
        "text": result.text,
        "confidence": result.confidence,
        "is_handwritten": result.is_handwritten,
    }


async def analytics_task_handler(task: Task) -> None:
    event_type = task.payload.get("event_type")
    event_data = task.payload.get("data", {})

    from app.utils.logger import get_logger

    logger = get_logger(__name__)
    logger.info(f"Analytics event: {event_type}", extra={"data": event_data})


async def notification_task_handler(task: Task) -> None:
    user_ids = task.payload.get("user_ids", [])
    message = task.payload.get("message", "")
    parse_mode = task.payload.get("parse_mode", "Markdown")

    from app.bot.dispatcher import get_bot

    bot = get_bot()
    for user_id in user_ids:
        try:
            await bot.send_message(
                chat_id=user_id, text=message, parse_mode=parse_mode
            )
            await asyncio.sleep(0.05)
        except Exception:
            continue


async def subscription_check_handler(task: Task) -> None:
    from datetime import datetime, timezone

    current_time = datetime.now(timezone.utc)
    task.payload["checked_at"] = current_time.isoformat()


def setup_task_handlers() -> None:
    queue = get_task_queue()
    queue.register_handler(TaskType.OCR, ocr_task_handler)
    queue.register_handler(TaskType.ANALYTICS, analytics_task_handler)
    queue.register_handler(TaskType.NOTIFICATION, notification_task_handler)
    queue.register_handler(TaskType.SUBSCRIPTION_CHECK, subscription_check_handler)
