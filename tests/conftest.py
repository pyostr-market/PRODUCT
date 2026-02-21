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

from src.core.auth.dependencies import get_current_user
from src.core.auth.schemas.user import TokenSchema, User, UserPermissionSchema
from src.core.db.database import Base, get_db
from src.core.services.images.storage import S3ImageStorageService
from src.mount import app

# ------------------------------
# CONTAINER (sync)
# ------------------------------

@pytest.fixture
def authorized_user():
    permissions_names = [
        'manufacturer:audit',
        'manufacturer:create',
        'manufacturer:update',
        'manufacturer:delete',
        'supplier:audit',
        'supplier:create',
        'supplier:update',
        'supplier:delete',
        'supplier:view',
        'category:audit',
        'category:create',
        'category:update',
        'category:delete',
        'product:audit',
        'product:create',
        'product:update',
        'product:delete',
        'product_type:audit',
        'product_type:create',
        'product_type:update',
        'product_type:delete',
        'product_attribute:audit',
        'product_attribute:create',
        'product_attribute:update',
        'product_attribute:delete',
    ]
    permissions = []
    for ids, name  in enumerate(permissions_names):
        permissions.append(
            UserPermissionSchema(id=ids, name=name),
        )
    return User(
        id=1,
        token_data=TokenSchema(
            exp=9999999999,
            iat=0,
            type="access"
        ),
        permissions=permissions
    )

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

    # ⬇️ ДОБАВИТЬ ЭТО
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


# ------------------------------
# CLIENT
# ------------------------------
@pytest_asyncio.fixture()
async def authorized_client(engine, authorized_user):

    async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    async def override_get_current_user():
        return authorized_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


class FakeImageStorage:
    def __init__(self):
        self.deleted_keys = []

    async def upload_bytes(self, *, data: bytes, key: str, content_type: str | None = None) -> None:
        return None

    async def delete_object(self, key: str) -> None:
        self.deleted_keys.append(key)

    def build_key(self, *, folder: str, filename: str) -> str:
        return f"{folder}/test-image-uuid.img"

    def build_public_url(self, key: str) -> str:
        return f"https://test-s3.local/{key}"


@pytest.fixture(autouse=True)
def image_storage_mock(monkeypatch):
    fake_storage = FakeImageStorage()
    monkeypatch.setattr(
        S3ImageStorageService,
        "from_settings",
        classmethod(lambda cls: fake_storage),
    )
    return fake_storage
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
