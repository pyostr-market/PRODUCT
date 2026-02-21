import pytest

from src.catalog.manufacturer.api.schemas.schemas import ManufacturerReadSchema

# =========================================================
# 200 — получение списка (доступно без авторизации)
# =========================================================

@pytest.mark.asyncio
async def test_filter_manufacturer_list_200(authorized_client, client):
    names = ["Apple", "Samsung", "Xiaomi"]

    # 1️⃣ Создаём данные (только авторизованный может)
    for name in names:
        r = await authorized_client.post(
            "/manufacturer",
            json={"name": name}
        )
        assert r.status_code == 200

    # 2️⃣ Получаем список БЕЗ авторизации
    response = await client.get("/manufacturer")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["total"] >= 3
    assert len(data["items"]) >= 3

    for item in data["items"]:
        ManufacturerReadSchema(**item)


# =========================================================
# Фильтрация по имени (без авторизации)
# =========================================================

@pytest.mark.asyncio
async def test_filter_manufacturer_by_name(authorized_client, client):
    await authorized_client.post("/manufacturer", json={"name": "FilterApple"})
    await authorized_client.post("/manufacturer", json={"name": "FilterSamsung"})
    await authorized_client.post("/manufacturer", json={"name": "OtherBrand"})

    response = await client.get("/manufacturer?name=Filter")
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
async def test_filter_manufacturer_limit(authorized_client, client):
    for i in range(5):
        await authorized_client.post(
            "/manufacturer",
            json={"name": f"LimitTest{i}"}
        )

    response = await client.get("/manufacturer?limit=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert len(data["items"]) == 2


# =========================================================
# Пагинация (offset)
# =========================================================

@pytest.mark.asyncio
async def test_filter_manufacturer_offset(authorized_client, client):
    for i in range(5):
        await authorized_client.post(
            "/manufacturer",
            json={"name": f"OffsetTest{i}"}
        )

    response = await client.get("/manufacturer?limit=2&offset=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert len(data["items"]) == 2


# =========================================================
# Пустой список
# =========================================================

@pytest.mark.asyncio
async def test_filter_manufacturer_empty(client):
    response = await client.get("/manufacturer?name=NoSuchBrand")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 0
    assert data["items"] == []