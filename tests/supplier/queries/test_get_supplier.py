import pytest

from src.catalog.suppliers.api.schemas.schemas import SupplierReadSchema


@pytest.mark.asyncio
async def test_get_supplier_200(authorized_client):
    create = await authorized_client.post(
        "/supplier",
        json={
            "name": "Get Test",
            "contact_email": "get@test.com",
            "phone": "+15557000",
        },
    )
    assert create.status_code == 200

    supplier_id = create.json()["data"]["id"]

    response = await authorized_client.get(f"/supplier/{supplier_id}")
    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert "data" in body

    supplier = SupplierReadSchema(**body["data"])

    assert supplier.id == supplier_id
    assert supplier.name == "Get Test"
    assert supplier.contact_email == "get@test.com"
    assert supplier.phone == "+15557000"


@pytest.mark.asyncio
async def test_get_supplier_404_not_found(authorized_client):
    response = await authorized_client.get("/supplier/999999")

    assert response.status_code == 404

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "supplier_not_found"


@pytest.mark.asyncio
async def test_get_supplier_403_no_permission():
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
            # Создаём поставщика через прямой доступ к БД (минуя API)
            async with async_session() as session:
                from src.catalog.suppliers.infrastructure.models.supplier import Supplier

                supplier = Supplier(
                    name="Permission Test",
                    contact_email="perm@test.com",
                    phone="+15550000",
                )
                session.add(supplier)
                await session.commit()
                supplier_id = supplier.id

            response = await ac.get(f"/supplier/{supplier_id}")
            assert response.status_code == 403

            body = response.json()
            assert body["success"] is False
            assert body["error"]["code"] == "forbidden"

        app.dependency_overrides.clear()
        await engine.dispose()
    finally:
        pg_container.stop()
