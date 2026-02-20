from __future__ import annotations

import json
import logging
import os
from typing import Any

from src.core.events.publisher import EventPublisher, NullEventPublisher

logger = logging.getLogger(__name__)


class RedisEventPublisher(EventPublisher):

    def __init__(
        self,
        *,
        host: str,
        port: int,
        password: str | None,
        db: int,
        channels: tuple[str, ...],
    ):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.channels = tuple(c for c in channels if c)
        self._client = None
        self._disabled = os.getenv("TESTING") == "1"

    async def _get_client(self):
        if self._disabled:
            return None

        if self._client is not None:
            return self._client

        try:
            from redis.asyncio import Redis
        except Exception:
            logger.warning("redis package not available; events publishing disabled")
            self._disabled = True
            return None

        try:
            self._client = Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                socket_connect_timeout=0.2,
                socket_timeout=0.2,
                retry_on_timeout=False,
                decode_responses=True,
            )
            await self._client.ping()
        except Exception:
            logger.exception("failed to connect to redis; events publishing disabled")
            self._disabled = True
            return None

        return self._client

    async def publish(self, message: dict[str, Any]) -> None:
        client = await self._get_client()
        if client is None:
            return None

        payload = json.dumps(message, ensure_ascii=False, default=str)

        try:
            for channel in self.channels:
                await client.publish(channel, payload)
        except Exception:
            logger.exception("failed to publish redis event")

    async def close(self) -> None:
        if self._client is None:
            return None
        await self._client.aclose()


def build_redis_or_null_publisher(
    *,
    host: str,
    port: int,
    password: str | None,
    db: int,
    channels: tuple[str, ...],
) -> EventPublisher:
    if not host or not port:
        return NullEventPublisher()

    return RedisEventPublisher(
        host=host,
        port=port,
        password=password,
        db=db,
        channels=channels,
    )
