import pytest

JPEG_BYTES = b"\xff\xd8\xff\xe0audit-image"


@pytest.mark.asyncio
async def test_audit_logs_after_create(authorized_client):
    create = await authorized_client.post(
        "/category",
        data={
            "name": "AuditCategory",
            "description": "Audit",
            "orderings": "0",
        },
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )

    assert create.status_code == 200
    category_id = create.json()["data"]["id"]

    response = await authorized_client.get("/category/admin/audit")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] >= 1

    log = data["items"][0]

    assert log["category_id"] == category_id
    assert log["action"] == "create"
    assert log["new_data"]["name"] == "AuditCategory"
    assert log["old_data"] is None


@pytest.mark.asyncio
async def test_audit_filter_by_category_id(authorized_client):
    create = await authorized_client.post(
        "/category",
        data={
            "name": "FilterAuditCategory",
            "orderings": "0",
        },
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )

    category_id = create.json()["data"]["id"]

    response = await authorized_client.get(
        f"/category/admin/audit?category_id={category_id}",
    )

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 1

    for item in data["items"]:
        assert item["category_id"] == category_id


@pytest.mark.asyncio
async def test_audit_filter_by_action(authorized_client):
    """Фильтр audit-логов по action"""
    await authorized_client.post(
        "/category",
        data={"name": "ActionCategory", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )

    response = await authorized_client.get("/category/admin/audit?action=create")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] >= 1

    for item in data["items"]:
        assert item["action"] == "create"


@pytest.mark.asyncio
async def test_audit_pagination(authorized_client):
    """Пагинация audit-логов"""
    for i in range(5):
        await authorized_client.post(
            "/category",
            data={"name": f"PaginatedCategory{i}", "orderings": "0"},
            files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
        )

    response = await authorized_client.get("/category/admin/audit?limit=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert len(data["items"]) == 2

    response2 = await authorized_client.get("/category/admin/audit?limit=2&offset=2")
    assert response2.status_code == 200

    data2 = response2.json()["data"]
    assert len(data2["items"]) == 2
