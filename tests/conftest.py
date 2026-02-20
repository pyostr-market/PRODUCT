import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["TESTING"] = "1"

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from src.core.db.database import Base, get_db
from src.mount import app

# ------------------------------
# CONTAINER (sync)
# ------------------------------

@pytest.fixture(scope="session")
def pg_container():
    container = PostgresContainer("postgres:18")
    container.start()
    yield container
    container.stop()

# ------------------------------
# ENGINE (function scope!)
# ------------------------------

@pytest_asyncio.fixture()
async def engine(pg_container):
    url = pg_container.get_connection_url().replace(
        "psycopg2", "asyncpg"
    )

    engine = create_async_engine(
        url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


# ------------------------------
# CLIENT
# ------------------------------

@pytest_asyncio.fixture()
async def client(engine):

    async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
