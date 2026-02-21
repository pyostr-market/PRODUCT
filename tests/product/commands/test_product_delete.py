import pytest


@pytest.mark.asyncio
async def test_delete_product_200(authorized_client):
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Удаляемый товар",
            "price": "300.00",
        },
    )
    assert create.status_code == 200

    product_id = create.json()["data"]["id"]

    response = await authorized_client.delete(f"/product/{product_id}")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_delete_product_404_not_found(authorized_client):
    response = await authorized_client.delete("/product/999999")

    assert response.status_code == 404

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_not_found"
