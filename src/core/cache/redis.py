import json
from typing import Any, Optional


class RedisCache:

    def __init__(self, redis_client):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        data = await self.redis.get(key)
        if not data:
            return None
        return json.loads(data)

    async def set(self, key: str, value: Any, ttl: int | None = None):
        payload = json.dumps(value)
        await self.redis.set(key, payload, ex=ttl)

    async def delete(self, key: str):
        await self.redis.delete(key)