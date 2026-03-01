import pytest


@pytest.mark.asyncio
async def test_delete_supplier_200(authorized_client):
    create = await authorized_client.post(
        "/supplier",
        json={
            "name": "Delete Me",
            "contact_email": "delete@test.com",
            "phone": "+15555000",
        },
    )

    assert create.status_code == 200
    supplier_id = create.json()["data"]["id"]

    response = await authorized_client.delete(f"/supplier/{supplier_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True

    get_response = await authorized_client.get(f"/supplier/{supplier_id}")

    assert get_response.status_code == 404

    get_body = get_response.json()
    assert get_body["success"] is False
    assert get_body["error"]["code"] == "supplier_not_found"


@pytest.mark.asyncio
async def test_delete_supplier_404_not_found(authorized_client):
    response = await authorized_client.delete("/supplier/999999")

    assert response.status_code == 404

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "supplier_not_found"


@pytest.mark.asyncio
async def test_delete_supplier_second_time_404(authorized_client):
    create = await authorized_client.post(
        "/supplier",
        json={
            "name": "Delete Twice",
            "contact_email": "twice@test.com",
            "phone": "+15556000",
        },
    )

    supplier_id = create.json()["data"]["id"]

    first_delete = await authorized_client.delete(f"/supplier/{supplier_id}")
    assert first_delete.status_code == 200

    second_delete = await authorized_client.delete(f"/supplier/{supplier_id}")

    assert second_delete.status_code == 404

    body = second_delete.json()
    assert body["success"] is False
    assert body["error"]["code"] == "supplier_not_found"
