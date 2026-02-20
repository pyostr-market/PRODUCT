from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from src.core.conf.settings import get_settings

Base = declarative_base()


# ============================================================
# ENGINE (создаётся лениво)
# ============================================================

@lru_cache
def get_async_engine() -> AsyncEngine:
    settings = get_settings()

    database_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_DB}"
    )

    return create_async_engine(
        database_url,
        echo=False,
        future=True,
    )
def get_sync_engine():
    settings = get_settings()
    SYNC_DATABASE_URL = (
        f"postgresql+psycopg2://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_DB}"
    )


    sync_engine = create_engine(
        SYNC_DATABASE_URL,
        echo=False,
    )
    return sync_engine

@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_async_engine(),
        expire_on_commit=False,
    )


# ============================================================
# DEPENDENCY
# ============================================================

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session
