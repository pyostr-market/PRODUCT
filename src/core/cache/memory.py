import time
from typing import Any, Optional


class InMemoryCache:

    def __init__(self):
        self._store: dict[str, tuple[Any, float | None]] = {}

    async def get(self, key: str) -> Optional[Any]:
        value = self._store.get(key)
        if not value:
            return None

        data, expires_at = value

        if expires_at and expires_at < time.time():
            del self._store[key]
            return None

        return data

    async def set(self, key: str, value: Any, ttl: int | None = None):
        expires_at = time.time() + ttl if ttl else None
        self._store[key] = (value, expires_at)

    async def delete(self, key: str):
        self._store.pop(key, None)