import pytest

from src.catalog.manufacturer.api.schemas.schemas import ManufacturerReadSchema

# =========================================================
# 200 — успешное обновление (имя + описание)
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_200_full_update(authorized_client):
    # Создаём производителя
    create = await authorized_client.post(
        "/manufacturer",
        json={
            "name": "Old Name",
            "description": "Old Description"
        }
    )

    assert create.status_code == 200
    created = create.json()["data"]

    manufacturer_id = created["id"]

    # Обновляем
    response = await authorized_client.put(
        f"/manufacturer/{manufacturer_id}",
        json={
            "name": "New Name",
            "description": "New Description"
        }
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body

    updated = ManufacturerReadSchema(**body["data"])

    assert updated.id == manufacturer_id
    assert updated.name == "New Name"
    assert updated.description == "New Description"


# =========================================================
# 200 — частичное обновление (только description)
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_200_partial_update(authorized_client):
    create = await authorized_client.post(
        "/manufacturer",
        json={
            "name": "Partial Name",
            "description": "Old Description"
        }
    )

    manufacturer_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/manufacturer/{manufacturer_id}",
        json={
            "description": "Updated Description"
        }
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    updated = ManufacturerReadSchema(**body["data"])

    assert updated.name == "Partial Name"  # имя не изменилось
    assert updated.description == "Updated Description"


# =========================================================
# 404 — производитель не найден
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_404_not_found(authorized_client):
    response = await authorized_client.put(
        "/manufacturer/999999",
        json={
            "name": "Does not exist"
        }
    )

    assert response.status_code == 404

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "manufacturer_not_found"


# =========================================================
# 400 — имя слишком короткое
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_400_name_too_short(authorized_client):
    create = await authorized_client.post(
        "/manufacturer",
        json={
            "name": "Valid Name",
            "description": "Desc"
        }
    )

    manufacturer_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/manufacturer/{manufacturer_id}",
        json={
            "name": "A"  # слишком короткое
        }
    )

    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "manufacturer_name_too_short"


# =========================================================
# 409 — конфликт уникальности
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_409_conflict(authorized_client):
    # Создаём двух производителей
    first = await authorized_client.post(
        "/manufacturer",
        json={
            "name": "Brand A",
            "description": "Desc A"
        }
    )

    second = await authorized_client.post(
        "/manufacturer",
        json={
            "name": "Brand B",
            "description": "Desc B"
        }
    )

    first_id = first.json()["data"]["id"]
    second_id = second.json()["data"]["id"]

    # Пытаемся переименовать второго в имя первого
    response = await authorized_client.put(
        f"/manufacturer/{second_id}",
        json={
            "name": "Brand A"
        }
    )

    assert response.status_code == 409

    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "manufacturer_already_exist"