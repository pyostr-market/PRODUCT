import pytest

from src.catalog.manufacturer.api.schemas.schemas import ManufacturerReadSchema

# =========================================================
# Получение списка
# =========================================================

@pytest.mark.asyncio
async def test_filter_manufacturer_list(client):
    # Создаём 3 производителя
    names = ["Apple", "Samsung", "Xiaomi"]

    for name in names:
        await client.post(
            "/manufacturer/",
            json={"name": name}
        )

    response = await client.get("/manufacturer/")

    assert response.status_code == 200

    body = response.json()

    assert body["success"] is True
    assert "data" in body

    data = body["data"]

    assert "total" in data
    assert "items" in data

    assert data["total"] >= 3
    assert len(data["items"]) >= 3

    # Проверяем валидацию схемы
    for item in data["items"]:
        ManufacturerReadSchema(**item)


# =========================================================
# Фильтрация по имени
# =========================================================

@pytest.mark.asyncio
async def test_filter_manufacturer_by_name(client):
    await client.post("/manufacturer/", json={"name": "FilterApple"})
    await client.post("/manufacturer/", json={"name": "FilterSamsung"})
    await client.post("/manufacturer/", json={"name": "OtherBrand"})

    response = await client.get("/manufacturer/?name=Filter")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2

    names = [item["name"] for item in data["items"]]

    assert "FilterApple" in names
    assert "FilterSamsung" in names
    assert "OtherBrand" not in names


# =========================================================
# Пагинация (limit)
# =========================================================

@pytest.mark.asyncio
async def test_filter_manufacturer_limit(client):
    for i in range(5):
        await client.post("/manufacturer/", json={"name": f"LimitTest{i}"})

    response = await client.get("/manufacturer/?limit=2")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert len(data["items"]) == 2


# =========================================================
# Пагинация (offset)
# =========================================================

@pytest.mark.asyncio
async def test_filter_manufacturer_offset(client):
    for i in range(5):
        await client.post("/manufacturer/", json={"name": f"OffsetTest{i}"})

    response = await client.get("/manufacturer/?limit=2&offset=2")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert len(data["items"]) == 2


# =========================================================
# Пустой список
# =========================================================

@pytest.mark.asyncio
async def test_filter_manufacturer_empty(client):
    response = await client.get("/manufacturer/?name=NoSuchBrand")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 0
    assert data["items"] == []