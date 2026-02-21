import pytest

from src.catalog.suppliers.api.schemas.schemas import SupplierReadSchema


@pytest.mark.asyncio
async def test_update_supplier_200_full_update(authorized_client):
    create = await authorized_client.post(
        "/supplier",
        json={
            "name": "Old Name",
            "contact_email": "old@test.com",
            "phone": "+15551000",
        },
    )

    assert create.status_code == 200
    created = create.json()["data"]
    supplier_id = created["id"]

    response = await authorized_client.put(
        f"/supplier/{supplier_id}",
        json={
            "name": "New Name",
            "contact_email": "new@test.com",
            "phone": "+15551001",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body

    updated = SupplierReadSchema(**body["data"])

    assert updated.id == supplier_id
    assert updated.name == "New Name"
    assert updated.contact_email == "new@test.com"
    assert updated.phone == "+15551001"


@pytest.mark.asyncio
async def test_update_supplier_200_partial_update(authorized_client):
    create = await authorized_client.post(
        "/supplier",
        json={
            "name": "Partial Name",
            "contact_email": "partial@test.com",
            "phone": "+15552000",
        },
    )

    supplier_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/supplier/{supplier_id}",
        json={
            "phone": "+15552001",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    updated = SupplierReadSchema(**body["data"])

    assert updated.name == "Partial Name"
    assert updated.contact_email == "partial@test.com"
    assert updated.phone == "+15552001"


@pytest.mark.asyncio
async def test_update_supplier_404_not_found(authorized_client):
    response = await authorized_client.put(
        "/supplier/999999",
        json={
            "name": "Does not exist",
        },
    )

    assert response.status_code == 404

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "supplier_not_found"


@pytest.mark.asyncio
async def test_update_supplier_400_name_too_short(authorized_client):
    create = await authorized_client.post(
        "/supplier",
        json={
            "name": "Valid Name",
            "contact_email": "valid@test.com",
            "phone": "+15553000",
        },
    )

    supplier_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/supplier/{supplier_id}",
        json={
            "name": "A",
        },
    )

    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "supplier_name_too_short"


@pytest.mark.asyncio
async def test_update_supplier_409_conflict(authorized_client):
    first = await authorized_client.post(
        "/supplier",
        json={
            "name": "Brand A",
            "contact_email": "a@test.com",
            "phone": "+15554000",
        },
    )

    second = await authorized_client.post(
        "/supplier",
        json={
            "name": "Brand B",
            "contact_email": "b@test.com",
            "phone": "+15554001",
        },
    )

    second_id = second.json()["data"]["id"]

    response = await authorized_client.put(
        f"/supplier/{second_id}",
        json={
            "name": "Brand A",
        },
    )

    assert response.status_code == 409

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "supplier_already_exist"
