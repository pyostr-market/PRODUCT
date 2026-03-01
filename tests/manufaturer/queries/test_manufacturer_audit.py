import pytest
import pytest_asyncio

from src.core.auth.schemas.user import TokenSchema, User, UserPermissionSchema


@pytest.fixture
def audit_user():
    permissions_names = [
        "manufacturer:audit",
        "manufacturer:create",
        "manufacturer:update",
        "manufacturer:delete",
    ]

    permissions = [
        UserPermissionSchema(id=i, name=name)
        for i, name in enumerate(permissions_names)
    ]

    return User(
        id=99,
        token_data=TokenSchema(exp=9999999999, iat=0, type="access"),
        permissions=permissions,
    )


@pytest_asyncio.fixture
async def audit_client(engine, audit_user):
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from src.core.auth.dependencies import get_current_user
    from src.core.db.database import get_db
    from src.mount import app

    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def override_get_db():
        async with async_session() as session:
            yield session

    async def override_get_current_user():
        return audit_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_audit_logs_after_create(audit_client):
    """200 — audit логи после создания производителя"""
    create = await audit_client.post(
        "/manufacturer",
        json={"name": "AuditBrand", "description": "Audit Description"}
    )
    assert create.status_code == 200

    manufacturer_id = create.json()["data"]["id"]

    response = await audit_client.get("/manufacturer/admin/audit")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["total"] >= 1

    log = data["items"][0]
    assert log["manufacturer_id"] == manufacturer_id
    assert log["action"] == "create"
    assert log["new_data"]["name"] == "AuditBrand"
    assert log["old_data"] is None


@pytest.mark.asyncio
async def test_audit_filter_by_manufacturer_id(audit_client):
    """Фильтр audit-логов по manufacturer_id"""
    create = await audit_client.post(
        "/manufacturer",
        json={"name": "FilterAuditBrand"}
    )
    manufacturer_id = create.json()["data"]["id"]

    response = await audit_client.get(f"/manufacturer/admin/audit?manufacturer_id={manufacturer_id}")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] >= 1

    for item in data["items"]:
        assert item["manufacturer_id"] == manufacturer_id


@pytest.mark.asyncio
async def test_audit_filter_by_action(audit_client):
    """Фильтр audit-логов по action"""
    await audit_client.post("/manufacturer", json={"name": "ActionBrand"})

    response = await audit_client.get("/manufacturer/admin/audit?action=create")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] >= 1

    for item in data["items"]:
        assert item["action"] == "create"


@pytest.mark.asyncio
async def test_audit_filter_by_user_id(audit_client, audit_user):
    """Фильтр audit-логов по user_id"""
    await audit_client.post("/manufacturer", json={"name": "UserFilterBrand"})

    response = await audit_client.get(f"/manufacturer/admin/audit?user_id={audit_user.id}")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] >= 1

    for item in data["items"]:
        assert item["user_id"] == audit_user.id


@pytest.mark.asyncio
async def test_audit_pagination(audit_client):
    """Пагинация audit-логов"""
    # Создаём несколько производителей
    for i in range(5):
        await audit_client.post("/manufacturer", json={"name": f"PaginatedBrand{i}"})

    response = await audit_client.get("/manufacturer/admin/audit?limit=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert len(data["items"]) == 2

    response2 = await audit_client.get("/manufacturer/admin/audit?limit=2&offset=2")
    assert response2.status_code == 200

    data2 = response2.json()["data"]
    assert len(data2["items"]) == 2


@pytest.mark.asyncio
async def test_audit_403_without_permission():
    """403 — нет permission manufacturer:audit"""
    from httpx import ASGITransport, AsyncClient
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from src.core.auth.dependencies import get_current_user
    from src.core.auth.schemas.user import TokenSchema, User
    from src.core.db.database import get_db
    from src.mount import app

    # Пользователь без manufacturer:audit
    user = User(
        id=100,
        token_data=TokenSchema(exp=9999999999, iat=0, type="access"),
        permissions=[],
    )

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/manufacturer/admin/audit")
        assert response.status_code == 403

    app.dependency_overrides.clear()
