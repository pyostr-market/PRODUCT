import pytest
import pytest_asyncio


@pytest.fixture
def audit_user():
    from src.core.auth.schemas.user import User, TokenSchema, UserPermissionSchema

    permissions_names = [
        "supplier:audit",
        "supplier:create",
        "supplier:update",
        "supplier:delete",
    ]

    permissions = [
        UserPermissionSchema(id=i, name=name)
        for i, name in enumerate(permissions_names)
    ]

    return User(
        id=99,
        token_data=TokenSchema(
            exp=9999999999,
            iat=0,
            type="access",
        ),
        permissions=permissions,
    )


@pytest_asyncio.fixture
async def audit_client(engine, audit_user):
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from httpx import ASGITransport, AsyncClient
    from src.mount import app
    from src.core.db.database import get_db
    from src.core.auth.dependencies import get_current_user

    async_session = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async def override_get_db():
        async with async_session() as session:
            yield session

    async def override_get_current_user():
        return audit_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_audit_logs_after_create(audit_client):
    create = await audit_client.post(
        "/supplier/",
        json={
            "name": "AuditBrand",
            "contact_email": "audit@test.com",
            "phone": "+15558000",
        },
    )

    assert create.status_code == 200

    supplier_id = create.json()["data"]["id"]

    response = await audit_client.get("/supplier/admin/audit")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["total"] >= 1

    log = data["items"][0]

    assert log["supplier_id"] == supplier_id
    assert log["action"] == "create"
    assert log["new_data"]["name"] == "AuditBrand"
    assert log["old_data"] is None


@pytest_asyncio.fixture
async def test_audit_filter_by_supplier_id(audit_client):
    create = await audit_client.post(
        "/supplier/",
        json={"name": "FilterAuditBrand"},
    )

    supplier_id = create.json()["data"]["id"]

    response = await audit_client.get(
        f"/supplier/admin/audit?supplier_id={supplier_id}",
    )

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 1

    for item in data["items"]:
        assert item["supplier_id"] == supplier_id


@pytest_asyncio.fixture
async def test_audit_filter_by_action(audit_client):
    await audit_client.post(
        "/supplier/",
        json={"name": "ActionBrand"},
    )

    response = await audit_client.get(
        "/supplier/admin/audit?action=create",
    )

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 1

    for item in data["items"]:
        assert item["action"] == "create"


@pytest_asyncio.fixture
async def test_audit_403_without_permission(authorized_client):
    response = await authorized_client.get("/supplier/admin/audit")

    assert response.status_code == 403
