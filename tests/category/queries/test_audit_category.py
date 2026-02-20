import pytest


@pytest.mark.asyncio
async def test_audit_logs_after_create(authorized_client):
    create = await authorized_client.post(
        "/category/",
        json={
            "name": "AuditCategory",
            "description": "Audit",
            "images": [
                {
                    "image": "audit-image",
                    "image_name": "test.jpg",
                    "ordering": 0,
                }
            ],
        },
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
        "/category/",
        json={
            "name": "FilterAuditCategory",
            "images": [
                {
                    "image": "audit-image",
                    "image_name": "test.jpg",
                    "ordering": 0,
                }
            ],
        },
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
