import pytest

from src.catalog.manufacturer.api.schemas.schemas import ManufacturerReadSchema

# =========================================================
# 200 — получить производителя по ID
# =========================================================

@pytest.mark.asyncio
async def test_get_manufacturer_200(client):
    # Создаём
    create = await client.post(
        "/manufacturer/",
        json={
            "name": "Get Test",
            "description": "Get Description"
        }
    )

    manufacturer_id = create.json()["data"]["id"]

    # Получаем
    response = await client.get(f"/manufacturer/{manufacturer_id}")

    assert response.status_code == 200

    body = response.json()

    # Контракт API
    assert body["success"] is True
    assert "data" in body
    assert "error" not in body

    manufacturer = ManufacturerReadSchema(**body["data"])

    assert manufacturer.id == manufacturer_id
    assert manufacturer.name == "Get Test"
    assert manufacturer.description == "Get Description"


# =========================================================
# 404 — производитель не найден
# =========================================================

@pytest.mark.asyncio
async def test_get_manufacturer_404_not_found(client):
    response = await client.get("/manufacturer/999999")

    assert response.status_code == 404

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "manufacturer_not_found"