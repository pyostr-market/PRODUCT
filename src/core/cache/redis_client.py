from redis.asyncio import Redis

from src.core.conf.settings import get_settings


class RedisClientFactory:

    _client: Redis | None = None

    @classmethod
    def get_client(cls) -> Redis:
        settings = get_settings()
        if cls._client is None:
            cls._client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,  # важно для json
            )
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None