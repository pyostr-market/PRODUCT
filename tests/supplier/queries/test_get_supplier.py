import pytest

from src.catalog.suppliers.api.schemas.schemas import SupplierReadSchema


@pytest.mark.asyncio
async def test_get_supplier_200(authorized_client, client):
    create = await authorized_client.post(
        "/supplier/",
        json={
            "name": "Get Test",
            "contact_email": "get@test.com",
            "phone": "+15557000",
        },
    )
    assert create.status_code == 200

    supplier_id = create.json()["data"]["id"]

    response = await client.get(f"/supplier/{supplier_id}")
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
async def test_get_supplier_404_not_found(client):
    response = await client.get("/supplier/999999")

    assert response.status_code == 404

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "supplier_not_found"
