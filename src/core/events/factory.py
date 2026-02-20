from __future__ import annotations

from functools import lru_cache

from src.core.conf.settings import get_settings
from src.core.events.bus import AsyncEventBus
from src.core.events.redis_publisher import build_redis_or_null_publisher


@lru_cache
def get_event_bus() -> AsyncEventBus:
    settings = get_settings()
    publisher = build_redis_or_null_publisher(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=settings.REDIS_DB,
        channels=tuple(
            channel
            for channel in (
                settings.REDIS_EVENTS_CHANNEL,
                settings.REDIS_USER_EVENTS_CHANNEL,
            )
            if channel
        ),
    )
    return AsyncEventBus(publisher=publisher)
