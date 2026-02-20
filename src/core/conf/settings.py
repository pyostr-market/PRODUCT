from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    def __init__(self, **values):
        from src.core.conf.bootstrap import bootstrap_env
        bootstrap_env()
        super().__init__(**values)
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

    # ===============================
    # JWT
    # ===============================

    JWT_ALGORITHM: str
    JWT_PRIVATE_KEY: str
    JWT_PUBLIC_KEY: str

    JWT_ACCESS_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7
    API_MODULES: list = [
        "src.core.api.api_module:CoreApiModule",
        "src.catalog.manufacturer.api_module:ManufacturerApiModule",
        "src.catalog.suppliers.api_module:SupplierApiModule",
    ]

@lru_cache
def get_settings() -> Settings:
    return Settings()
