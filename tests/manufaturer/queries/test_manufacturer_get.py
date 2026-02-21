import pytest

from src.catalog.manufacturer.api.schemas.schemas import ManufacturerReadSchema

# =========================================================
# 200 — получить производителя по ID (без авторизации)
# =========================================================

@pytest.mark.asyncio
async def test_get_manufacturer_200(authorized_client, client):
    # 1️⃣ Создаём (нужна авторизация)
    create = await authorized_client.post(
        "/manufacturer",
        json={
            "name": "Get Test",
            "description": "Get Description"
        }
    )
    assert create.status_code == 200

    manufacturer_id = create.json()["data"]["id"]

    # 2️⃣ Получаем БЕЗ авторизации
    response = await client.get(f"/manufacturer/{manufacturer_id}")
    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert "data" in body

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