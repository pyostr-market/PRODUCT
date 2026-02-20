import pytest


@pytest.mark.asyncio
async def test_product_audit_logs_200(authorized_client):
    create = await authorized_client.post(
        "/product/",
        data={
            "name": "Audit Product",
            "price": "10.00",
        },
    )
    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    update = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Audit Product Updated",
        },
    )
    assert update.status_code == 200

    response = await authorized_client.get(f"/product/admin/audit?product_id={product_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["total"] >= 2
    assert len(data["items"]) >= 2

    actions = [item["action"] for item in data["items"]]
    assert "create" in actions
    assert "update" in actions
