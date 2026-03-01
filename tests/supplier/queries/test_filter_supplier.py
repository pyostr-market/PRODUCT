import pytest

from src.catalog.suppliers.api.schemas.schemas import SupplierReadSchema


@pytest.mark.asyncio
async def test_filter_supplier_list_200(authorized_client):
    names = ["Apple", "Samsung", "Xiaomi"]

    for name in names:
        r = await authorized_client.post(
            "/supplier",
            json={"name": name},
        )
        assert r.status_code == 200

    response = await authorized_client.get("/supplier")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["total"] >= 3
    assert len(data["items"]) >= 3

    for item in data["items"]:
        SupplierReadSchema(**item)


@pytest.mark.asyncio
async def test_filter_supplier_by_name(authorized_client):
    await authorized_client.post("/supplier", json={"name": "FilterApple"})
    await authorized_client.post("/supplier", json={"name": "FilterSamsung"})
    await authorized_client.post("/supplier", json={"name": "OtherBrand"})

    response = await authorized_client.get("/supplier?name=Filter")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2

    names = [item["name"] for item in data["items"]]

    assert "FilterApple" in names
    assert "FilterSamsung" in names
    assert "OtherBrand" not in names


@pytest.mark.asyncio
async def test_filter_supplier_limit(authorized_client):
    for i in range(5):
        await authorized_client.post(
            "/supplier",
            json={"name": f"LimitTest{i}"},
        )

    response = await authorized_client.get("/supplier?limit=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_filter_supplier_offset(authorized_client):
    for i in range(5):
        await authorized_client.post(
            "/supplier",
            json={"name": f"OffsetTest{i}"},
        )

    response = await authorized_client.get("/supplier?limit=2&offset=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_filter_supplier_empty(authorized_client):
    response = await authorized_client.get("/supplier?name=NoSuchBrand")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_filter_supplier_403_no_permission():
    """403 — нет permission supplier:view"""
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from testcontainers.postgres import PostgresContainer

    from src.core.auth.dependencies import get_current_user
    from src.core.auth.schemas.user import TokenSchema, User, UserPermissionSchema
    from src.core.db.database import Base, get_db
    from src.mount import app

    pg_container = PostgresContainer("postgres:18")
    pg_container.start()

    try:
        url = pg_container.get_connection_url().replace("psycopg2", "asyncpg")
        engine = create_async_engine(url, echo=False, future=True)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

        async def override_get_db():
            async with async_session() as session:
                yield session

        # Пользователь без supplier:view
        permissions = [
            UserPermissionSchema(id=1, name="supplier:create"),
            UserPermissionSchema(id=2, name="supplier:update"),
            UserPermissionSchema(id=3, name="supplier:delete"),
        ]
        user = User(
            id=1,
            token_data=TokenSchema(exp=9999999999, iat=0, type="access"),
            permissions=permissions,
        )

        async def override_get_current_user():
            return user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user

        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/supplier")
            assert response.status_code == 403

            body = response.json()
            assert body["success"] is False
            assert body["error"]["code"] == "forbidden"

        app.dependency_overrides.clear()
        await engine.dispose()
    finally:
        pg_container.stop()
