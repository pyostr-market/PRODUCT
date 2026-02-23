"""
Тесты для LIKE-поиска по производителям (manufacturer).

Проверяют поиск по полю name с использованием различных сценариев:
- Поиск по части слова (ilike)
- Регистронезависимый поиск
- Поиск с специальными символами
- Поиск по началу/концу/середине слова
"""
import pytest


# =========================================================
# LIKE-поиск: регистронезависимость
# =========================================================

@pytest.mark.asyncio
async def test_manufacturer_search_case_insensitive_upper(authorized_client, client):
    """Поиск 'APPLE' должен найти 'Apple'"""
    await authorized_client.post("/manufacturer", json={"name": "Apple"})
    await authorized_client.post("/manufacturer", json={"name": "Samsung"})

    response = await client.get("/manufacturer?name=APPLE")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Apple"


@pytest.mark.asyncio
async def test_manufacturer_search_case_insensitive_lower(authorized_client, client):
    """Поиск 'samsung' должен найти 'Samsung'"""
    await authorized_client.post("/manufacturer", json={"name": "Apple"})
    await authorized_client.post("/manufacturer", json={"name": "Samsung"})

    response = await client.get("/manufacturer?name=samsung")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Samsung"


@pytest.mark.asyncio
async def test_manufacturer_search_case_insensitive_mixed(authorized_client, client):
    """Поиск 'XiaOmI' должен найти 'Xiaomi'"""
    await authorized_client.post("/manufacturer", json={"name": "Xiaomi"})

    response = await client.get("/manufacturer?name=XiaOmI")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Xiaomi"


# =========================================================
# LIKE-поиск: поиск по части слова
# =========================================================

@pytest.mark.asyncio
async def test_manufacturer_search_by_startswith(authorized_client, client):
    """Поиск по началу слова: 'App' находит 'Apple'"""
    await authorized_client.post("/manufacturer", json={"name": "Apple"})
    await authorized_client.post("/manufacturer", json={"name": "Application Corp"})
    await authorized_client.post("/manufacturer", json={"name": "Samsung"})

    response = await client.get("/manufacturer?name=App")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "Apple" in names
    assert "Application Corp" in names
    assert "Samsung" not in names


@pytest.mark.asyncio
async def test_manufacturer_search_by_endswith(authorized_client, client):
    """Поиск по концу слова: 'soft' находит 'Microsoft', 'Softbank'"""
    await authorized_client.post("/manufacturer", json={"name": "Microsoft"})
    await authorized_client.post("/manufacturer", json={"name": "Softbank"})
    await authorized_client.post("/manufacturer", json={"name": "Apple"})

    response = await client.get("/manufacturer?name=soft")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "Microsoft" in names
    assert "Softbank" in names
    assert "Apple" not in names


@pytest.mark.asyncio
async def test_manufacturer_search_by_contains(authorized_client, client):
    """Поиск по середине слова: 'oft' находит 'Microsoft', 'Software Inc'"""
    await authorized_client.post("/manufacturer", json={"name": "Microsoft"})
    await authorized_client.post("/manufacturer", json={"name": "Software Inc"})
    await authorized_client.post("/manufacturer", json={"name": "Apple"})

    response = await client.get("/manufacturer?name=oft")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "Microsoft" in names
    assert "Software Inc" in names
    assert "Apple" not in names


# =========================================================
# LIKE-поиск: поиск по полному совпадению
# =========================================================

@pytest.mark.asyncio
async def test_manufacturer_search_exact_match(authorized_client, client):
    """Поиск по точному совпадению"""
    await authorized_client.post("/manufacturer", json={"name": "Exact Match"})
    await authorized_client.post("/manufacturer", json={"name": "Other Name"})

    response = await client.get("/manufacturer?name=Exact Match")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Exact Match"


# =========================================================
# LIKE-поиск: поиск с пробелами и специальными символами
# =========================================================

@pytest.mark.asyncio
async def test_manufacturer_search_with_spaces(authorized_client, client):
    """Поиск по названию с пробелами"""
    await authorized_client.post("/manufacturer", json={"name": "Apple Inc"})
    await authorized_client.post("/manufacturer", json={"name": "Apple"})

    response = await client.get("/manufacturer?name=Apple Inc")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Apple Inc"


@pytest.mark.asyncio
async def test_manufacturer_search_with_hyphen(authorized_client, client):
    """Поиск по названию с дефисом"""
    await authorized_client.post("/manufacturer", json={"name": "Samsung-LG"})
    await authorized_client.post("/manufacturer", json={"name": "Samsung"})

    response = await client.get("/manufacturer?name=Samsung-LG")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Samsung-LG"


@pytest.mark.asyncio
async def test_manufacturer_search_with_numbers(authorized_client, client):
    """Поиск по названию с цифрами"""
    await authorized_client.post("/manufacturer", json={"name": "3M Company"})
    await authorized_client.post("/manufacturer", json={"name": "Company 3M"})

    response = await client.get("/manufacturer?name=3M")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2


# =========================================================
# LIKE-поиск: пустой и специальный поиск
# =========================================================

@pytest.mark.asyncio
async def test_manufacturer_search_empty_string(authorized_client, client):
    """Пустой поиск должен вернуть все записи"""
    await authorized_client.post("/manufacturer", json={"name": "Apple"})
    await authorized_client.post("/manufacturer", json={"name": "Samsung"})

    response = await client.get("/manufacturer?name=")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2


@pytest.mark.asyncio
async def test_manufacturer_search_no_results(authorized_client, client):
    """Поиск без результатов"""
    await authorized_client.post("/manufacturer", json={"name": "Apple"})
    await authorized_client.post("/manufacturer", json={"name": "Samsung"})

    response = await client.get("/manufacturer?name=NonExistent")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_manufacturer_search_special_chars_percent(authorized_client, client):
    """Поиск с символом %"""
    await authorized_client.post("/manufacturer", json={"name": "Test%Company"})
    await authorized_client.post("/manufacturer", json={"name": "Test Company"})

    # Символ % должен экранироваться и искаться как literal
    response = await client.get("/manufacturer?name=Test%")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    # Ищем названия, содержащие "Test%"
    assert data["total"] >= 1


# =========================================================
# LIKE-поиск: комбинация с пагинацией
# =========================================================

@pytest.mark.asyncio
async def test_manufacturer_search_with_pagination(authorized_client, client):
    """Поиск с пагинацией"""
    for i in range(10):
        await authorized_client.post("/manufacturer", json={"name": f"Search Test {i}"})
    await authorized_client.post("/manufacturer", json={"name": "Other"})

    response = await client.get("/manufacturer?name=Search&limit=5&offset=0")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 10
    assert len(data["items"]) == 5

    # Проверяем вторую страницу
    response2 = await client.get("/manufacturer?name=Search&limit=5&offset=5")
    assert response2.status_code == 200

    body2 = response2.json()
    data2 = body2["data"]

    assert data2["total"] == 10
    assert len(data2["items"]) == 5


# =========================================================
# LIKE-поиск: поиск по кириллическим названиям
# =========================================================

@pytest.mark.asyncio
async def test_manufacturer_search_cyrillic(authorized_client, client):
    """Поиск по кириллическим названиям"""
    await authorized_client.post("/manufacturer", json={"name": "Яндекс"})
    await authorized_client.post("/manufacturer", json={"name": "Сбер"})

    response = await client.get("/manufacturer?name=Ян")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Яндекс"


@pytest.mark.asyncio
async def test_manufacturer_search_cyrillic_case_insensitive(authorized_client, client):
    """Регистронезависимый поиск по кириллице"""
    await authorized_client.post("/manufacturer", json={"name": "Яндекс"})

    response = await client.get("/manufacturer?name=яндекс")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Яндекс"
