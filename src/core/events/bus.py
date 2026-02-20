from __future__ import annotations

import asyncio
import logging
from typing import Any, Iterable

from src.core.events.publisher import EventPublisher

logger = logging.getLogger(__name__)


class AsyncEventBus:

    def __init__(self, publisher: EventPublisher):
        self.publisher = publisher

    def publish_nowait(self, message: dict[str, Any]) -> None:
        asyncio.create_task(self._publish_safe(message))

    def publish_many_nowait(self, messages: Iterable[dict[str, Any]]) -> None:
        for message in messages:
            asyncio.create_task(self._publish_safe(message))

    async def _publish_safe(self, message: dict[str, Any]) -> None:
        try:
            await self.publisher.publish(message)
        except Exception:
            logger.exception("failed to publish event")
