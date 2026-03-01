"""
Тесты для LIKE-поиска по типам продуктов (product_type).

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
async def test_product_type_search_case_insensitive_upper(authorized_client, client):
    """Поиск 'SMARTPHONE' должен найти 'Smartphone'"""
    await authorized_client.post("/product/type", json={"name": "Smartphone", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Laptop", "parent_id": None})

    response = await client.get("/product/type?name=SMARTPHONE")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Smartphone"


@pytest.mark.asyncio
async def test_product_type_search_case_insensitive_lower(authorized_client, client):
    """Поиск 'laptop' должен найти 'Laptop'"""
    await authorized_client.post("/product/type", json={"name": "Smartphone", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Laptop", "parent_id": None})

    response = await client.get("/product/type?name=laptop")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Laptop"


@pytest.mark.asyncio
async def test_product_type_search_case_insensitive_mixed(authorized_client, client):
    """Поиск 'TaBlEt' должен найти 'Tablet'"""
    await authorized_client.post("/product/type", json={"name": "Tablet", "parent_id": None})

    response = await client.get("/product/type?name=TaBlEt")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Tablet"


# =========================================================
# LIKE-поиск: поиск по части слова
# =========================================================

@pytest.mark.asyncio
async def test_product_type_search_by_startswith(authorized_client, client):
    """Поиск по началу слова: 'Ph' находит 'Phone', 'Phones'"""
    await authorized_client.post("/product/type", json={"name": "Phone", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Phones", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Tablet", "parent_id": None})

    response = await client.get("/product/type?name=Ph")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "Phone" in names
    assert "Phones" in names
    assert "Tablet" not in names


@pytest.mark.asyncio
async def test_product_type_search_by_endswith(authorized_client, client):
    """Поиск по концу слова: 'book' находит 'MacBook', 'Notebook'"""
    await authorized_client.post("/product/type", json={"name": "MacBook", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Notebook", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Desktop", "parent_id": None})

    response = await client.get("/product/type?name=book")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "MacBook" in names
    assert "Notebook" in names
    assert "Desktop" not in names


@pytest.mark.asyncio
async def test_product_type_search_by_contains(authorized_client, client):
    """Поиск по середине слова: 'hone' находит 'Phone', 'Phones'"""
    await authorized_client.post("/product/type", json={"name": "Phone", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Smartphone", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Tablet", "parent_id": None})

    response = await client.get("/product/type?name=hone")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "Phone" in names
    assert "Smartphone" in names
    assert "Tablet" not in names


# =========================================================
# LIKE-поиск: поиск по полному совпадению
# =========================================================

@pytest.mark.asyncio
async def test_product_type_search_exact_match(authorized_client, client):
    """Поиск по точному совпадению"""
    await authorized_client.post("/product/type", json={"name": "Exact Type", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Other Type", "parent_id": None})

    response = await client.get("/product/type?name=Exact Type")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Exact Type"


# =========================================================
# LIKE-поиск: поиск с пробелами и специальными символами
# =========================================================

@pytest.mark.asyncio
async def test_product_type_search_with_spaces(authorized_client, client):
    """Поиск по названию с пробелами"""
    await authorized_client.post("/product/type", json={"name": "Mobile Phone", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Mobile", "parent_id": None})

    response = await client.get("/product/type?name=Mobile Phone")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Mobile Phone"


@pytest.mark.asyncio
async def test_product_type_search_with_hyphen(authorized_client, client):
    """Поиск по названию с дефисом"""
    await authorized_client.post("/product/type", json={"name": "All-in-One", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "All in One", "parent_id": None})

    response = await client.get("/product/type?name=All-in-One")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "All-in-One"


@pytest.mark.asyncio
async def test_product_type_search_with_slash(authorized_client, client):
    """Поиск по названию со слэшем"""
    await authorized_client.post("/product/type", json={"name": "Audio/Video", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Audio", "parent_id": None})

    response = await client.get("/product/type?name=Audio/Video")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Audio/Video"


@pytest.mark.asyncio
async def test_product_type_search_with_numbers(authorized_client, client):
    """Поиск по названию с цифрами"""
    await authorized_client.post("/product/type", json={"name": "3D Printer", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Printer 3D", "parent_id": None})

    response = await client.get("/product/type?name=3D")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2


# =========================================================
# LIKE-поиск: пустой и специальный поиск
# =========================================================

@pytest.mark.asyncio
async def test_product_type_search_empty_string(authorized_client, client):
    """Пустой поиск должен вернуть все записи"""
    await authorized_client.post("/product/type", json={"name": "Type A", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Type B", "parent_id": None})

    response = await client.get("/product/type?name=")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2


@pytest.mark.asyncio
async def test_product_type_search_no_results(authorized_client, client):
    """Поиск без результатов"""
    await authorized_client.post("/product/type", json={"name": "Type A", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Type B", "parent_id": None})

    response = await client.get("/product/type?name=NonExistent")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 0
    assert data["items"] == []


# =========================================================
# LIKE-поиск: комбинация с пагинацией
# =========================================================

@pytest.mark.asyncio
async def test_product_type_search_with_pagination(authorized_client, client):
    """Поиск с пагинацией"""
    for i in range(10):
        await authorized_client.post("/product/type", json={"name": f"Search Test Type {i}", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Other Type", "parent_id": None})

    response = await client.get("/product/type?name=Search&limit=5&offset=0")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 10
    assert len(data["items"]) == 5

    # Проверяем вторую страницу
    response2 = await client.get("/product/type?name=Search&limit=5&offset=5")
    assert response2.status_code == 200

    body2 = response2.json()
    data2 = body2["data"]

    assert data2["total"] == 10
    assert len(data2["items"]) == 5


# =========================================================
# LIKE-поиск: поиск по кириллическим названиям
# =========================================================

@pytest.mark.asyncio
async def test_product_type_search_cyrillic(authorized_client, client):
    """Поиск по кириллическим названиям"""
    await authorized_client.post("/product/type", json={"name": "Смартфон", "parent_id": None})
    await authorized_client.post("/product/type", json={"name": "Ноутбук", "parent_id": None})

    response = await client.get("/product/type?name=Смар")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Смартфон"


@pytest.mark.asyncio
async def test_product_type_search_cyrillic_case_insensitive(authorized_client, client):
    """Регистронезависимый поиск по кириллице"""
    await authorized_client.post("/product/type", json={"name": "Смартфон", "parent_id": None})

    response = await client.get("/product/type?name=смартфон")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Смартфон"


# =========================================================
# LIKE-поиск: поиск с родительскими типами
# =========================================================

@pytest.mark.asyncio
async def test_product_type_search_with_parent(authorized_client, client):
    """Поиск дочерних типов продуктов"""
    # Создаём родительский тип
    parent_resp = await authorized_client.post("/product/type", json={"name": "Electronics", "parent_id": None})
    parent_id = parent_resp.json()["data"]["id"]

    # Создаём дочерние типы
    await authorized_client.post("/product/type", json={"name": "Phones", "parent_id": parent_id})
    await authorized_client.post("/product/type", json={"name": "Tablets", "parent_id": parent_id})
    await authorized_client.post("/product/type", json={"name": "Other", "parent_id": None})

    response = await client.get("/product/type?name=Ph")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Phones"
    assert data["items"][0]["parent"]["id"] == parent_id


# =========================================================
# LIKE-поиск: поиск иерархии типов
# =========================================================

@pytest.mark.asyncio
async def test_product_type_search_nested_hierarchy(authorized_client, client):
    """Поиск по иерархии типов продуктов"""
    # Создаём иерархию: Electronics -> Mobile -> Smartphone
    level1 = await authorized_client.post("/product/type", json={"name": "Electronics", "parent_id": None})
    level2 = await authorized_client.post("/product/type", json={"name": "Mobile", "parent_id": level1.json()["data"]["id"]})
    await authorized_client.post("/product/type", json={"name": "Smartphone", "parent_id": level2.json()["data"]["id"]})

    # Ищем по "Mobile"
    response = await client.get("/product/type?name=Mobile")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Mobile"
    assert data["items"][0]["parent"]["id"] == level1.json()["data"]["id"]
