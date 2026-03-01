from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    def __init__(self, **values):
        from src.core.conf.bootstrap import bootstrap_env
        bootstrap_env()
        super().__init__(**values)

    # ===============================
    # MODULES
    # ===============================

    API_MODULES: list = [
        "src.core.api.api_module:CoreApiModule",
        "src.uploads.api_module:UploadsApiModule",
        "src.catalog.manufacturer.api_module:ManufacturerApiModule",
        "src.catalog.suppliers.api_module:SupplierApiModule",
        "src.catalog.category.api_module:CategoryApiModule",
        "src.catalog.product.api_module:ProductApiModule",
    ]
    # ===============================
    # POSTGRES
    # ===============================

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_ASYNC_DRIVER: str

    # ===============================
    # REDIS
    # ===============================

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_EVENTS_CHANNEL: str = "catalog.events"
    REDIS_USER_EVENTS_CHANNEL: str = "product.events"
    REDIS_PUBSUB_ENABLED: bool = True
    REDIS_CONNECT_TIMEOUT_SECONDS: float = 0.2
    REDIS_SOCKET_TIMEOUT_SECONDS: float = 0.2

    # ===============================
    # JWT
    # ===============================

    JWT_ALGORITHM: str
    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str

    # ===============================
    # S3
    # ===============================

    BUCKET_NAME: str = '2481cb39-trade'
    S3_ACCESS_KEY: str
    S3_SECRET_ACCESS_KEY: str
    S3_URL: str = 'https://s3.twcstorage.ru'
    S3_REGION: str = 'ru-1'

@lru_cache
def get_settings() -> Settings:
    return Settings()
