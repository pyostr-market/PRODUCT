import pytest

from src.catalog.suppliers.api.schemas.schemas import SupplierReadSchema


@pytest.mark.asyncio
async def test_create_supplier_200(authorized_client):
    response = await authorized_client.post(
        "/supplier/",
        json={
            "name": "Apple поставщик",
            "contact_email": "apple@test.com",
            "phone": "+15550001",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "error" not in body

    supplier = SupplierReadSchema(**body["data"])

    assert supplier.name == "Apple поставщик"
    assert supplier.contact_email == "apple@test.com"
    assert supplier.phone == "+15550001"
    assert isinstance(supplier.id, int)


@pytest.mark.asyncio
async def test_create_supplier_409_already_exists(authorized_client):
    payload = {
        "name": "Samsung",
        "contact_email": "samsung@test.com",
        "phone": "+15550002",
    }

    first = await authorized_client.post("/supplier/", json=payload)
    assert first.status_code == 200

    response = await authorized_client.post("/supplier/", json=payload)

    assert response.status_code == 409

    body = response.json()
    assert body["success"] is False
    assert "error" in body
    assert "data" not in body

    error = body["error"]
    assert error["code"] == "supplier_already_exist"
    assert isinstance(error["message"], str)
    assert isinstance(error["details"], dict)


@pytest.mark.asyncio
async def test_create_supplier_400_name_too_short(authorized_client):
    response = await authorized_client.post(
        "/supplier/",
        json={
            "name": "A",
            "contact_email": "short@test.com",
            "phone": "+15550003",
        },
    )

    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False
    assert "error" in body
    assert "data" not in body

    error = body["error"]
    assert error["code"] == "supplier_name_too_short"
    assert isinstance(error["message"], str)
    assert isinstance(error["details"], dict)
