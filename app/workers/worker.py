from __future__ import annotations

import asyncio
import signal
import sys

from app.config.settings import get_settings
from app.utils.logger import get_logger, setup_logging
from app.workers.tasks import TaskQueue, TaskType, get_task_queue, setup_task_handlers

settings = get_settings()
logger = get_logger(__name__)

_running = True


def signal_handler(sig: int, frame: object) -> None:
    global _running
    _running = False
    logger.info("Shutting down worker...")


async def worker_loop(queue: TaskQueue) -> None:
    while _running:
        try:
            processed = await queue.process_next()
            if not processed:
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
            await asyncio.sleep(1)


async def main() -> None:
    setup_logging()
    setup_task_handlers()
    queue = get_task_queue()

    logger.info(
        f"Starting worker (concurrency={settings.WORKER_CONCURRENCY})"
    )

    workers = [
        asyncio.create_task(worker_loop(queue))
        for _ in range(settings.WORKER_CONCURRENCY)
    ]

    await asyncio.gather(*workers)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
