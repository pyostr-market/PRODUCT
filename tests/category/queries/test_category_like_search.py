"""
Тесты для LIKE-поиска по категориям (category).

Проверяют поиск по полю name с использованием различных сценариев:
- Поиск по части слова (ilike)
- Регистронезависимый поиск
- Поиск с специальными символами
- Поиск по началу/концу/середине слова
"""
import pytest

JPEG_BYTES = b"\xff\xd8\xff\xe0test-image"


async def _create_category(client, name: str, parent_id: int = None, manufacturer_id: int = None):
    """Вспомогательная функция для создания категории."""
    data = {"name": name, "orderings": "0"}
    if parent_id:
        data["parent_id"] = str(parent_id)
    if manufacturer_id:
        data["manufacturer_id"] = str(manufacturer_id)
    
    return await client.post(
        "/category",
        data=data,
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )


# =========================================================
# LIKE-поиск: регистронезависимость
# =========================================================

@pytest.mark.asyncio
async def test_category_search_case_insensitive_upper(authorized_client, client):
    """Поиск 'ЭЛЕКТРОНИКА' должен найти 'Электроника'"""
    await _create_category(authorized_client, "Электроника")
    await _create_category(authorized_client, "Одежда")

    response = await client.get("/category?name=ЭЛЕКТРОНИКА")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Электроника"


@pytest.mark.asyncio
async def test_category_search_case_insensitive_lower(authorized_client, client):
    """Поиск 'electronics' должен найти 'Electronics'"""
    await _create_category(authorized_client, "Electronics")
    await _create_category(authorized_client, "Clothing")

    response = await client.get("/category?name=electronics")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Electronics"


@pytest.mark.asyncio
async def test_category_search_case_insensitive_mixed(authorized_client, client):
    """Поиск 'PhOnEs' должен найти 'Phones'"""
    await _create_category(authorized_client, "Phones")

    response = await client.get("/category?name=PhOnEs")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Phones"


# =========================================================
# LIKE-поиск: поиск по части слова
# =========================================================

@pytest.mark.asyncio
async def test_category_search_by_startswith(authorized_client, client):
    """Поиск по началу слова: 'Смар' находит 'Смартфоны'"""
    await _create_category(authorized_client, "Смартфоны")
    await _create_category(authorized_client, "Смарт-часы")
    await _create_category(authorized_client, "Ноутбуки")

    response = await client.get("/category?name=Смар")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "Смартфоны" in names
    assert "Смарт-часы" in names
    assert "Ноутбуки" not in names


@pytest.mark.asyncio
async def test_category_search_by_endswith(authorized_client, client):
    """Поиск по концу слова: 'фоны' находит 'Смартфоны'"""
    await _create_category(authorized_client, "Смартфоны")
    await _create_category(authorized_client, "Кнопочные телефоны")
    await _create_category(authorized_client, "Планшеты")

    response = await client.get("/category?name=фоны")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "Смартфоны" in names
    assert "Кнопочные телефоны" in names
    assert "Планшеты" not in names


@pytest.mark.asyncio
async def test_category_search_by_contains(authorized_client, client):
    """Поиск по середине слова: 'aptop' находит 'Laptops'"""
    await _create_category(authorized_client, "Laptops")
    await _create_category(authorized_client, "Laptop Accessories")
    await _create_category(authorized_client, "Desktops")

    response = await client.get("/category?name=aptop")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "Laptops" in names
    assert "Laptop Accessories" in names
    assert "Desktops" not in names


# =========================================================
# LIKE-поиск: поиск по полному совпадению
# =========================================================

@pytest.mark.asyncio
async def test_category_search_exact_match(authorized_client, client):
    """Поиск по точному совпадению"""
    await _create_category(authorized_client, "Exact Category")
    await _create_category(authorized_client, "Other Category")

    response = await client.get("/category?name=Exact Category")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Exact Category"


# =========================================================
# LIKE-поиск: поиск с пробелами и специальными символами
# =========================================================

@pytest.mark.asyncio
async def test_category_search_with_spaces(authorized_client, client):
    """Поиск по названию с пробелами"""
    await _create_category(authorized_client, "Mobile Phones")
    await _create_category(authorized_client, "Mobile")

    response = await client.get("/category?name=Mobile Phones")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Mobile Phones"


@pytest.mark.asyncio
async def test_category_search_with_hyphen(authorized_client, client):
    """Поиск по названию с дефисом"""
    await _create_category(authorized_client, "Smart-Home")
    await _create_category(authorized_client, "Smart Home")

    response = await client.get("/category?name=Smart-Home")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Smart-Home"


@pytest.mark.asyncio
async def test_category_search_with_slash(authorized_client, client):
    """Поиск по названию со слэшем"""
    await _create_category(authorized_client, "Audio/Video")
    await _create_category(authorized_client, "Audio")

    response = await client.get("/category?name=Audio/Video")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Audio/Video"


@pytest.mark.asyncio
async def test_category_search_with_numbers(authorized_client, client):
    """Поиск по названию с цифрами"""
    await _create_category(authorized_client, "3D Printers")
    await _create_category(authorized_client, "Printers 3D")

    response = await client.get("/category?name=3D")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2


# =========================================================
# LIKE-поиск: пустой и специальный поиск
# =========================================================

@pytest.mark.asyncio
async def test_category_search_empty_string(authorized_client, client):
    """Пустой поиск должен вернуть все записи"""
    await _create_category(authorized_client, "Category A")
    await _create_category(authorized_client, "Category B")

    response = await client.get("/category?name=")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2


@pytest.mark.asyncio
async def test_category_search_no_results(authorized_client, client):
    """Поиск без результатов"""
    await _create_category(authorized_client, "Category A")
    await _create_category(authorized_client, "Category B")

    response = await client.get("/category?name=NonExistent")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 0
    assert data["items"] == []


# =========================================================
# LIKE-поиск: комбинация с пагинацией
# =========================================================

@pytest.mark.asyncio
async def test_category_search_with_pagination(authorized_client, client):
    """Поиск с пагинацией"""
    for i in range(10):
        await _create_category(authorized_client, f"Search Test Category {i}")
    await _create_category(authorized_client, "Other Category")

    response = await client.get("/category?name=Search&limit=5&offset=0")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 10
    assert len(data["items"]) == 5

    # Проверяем вторую страницу
    response2 = await client.get("/category?name=Search&limit=5&offset=5")
    assert response2.status_code == 200

    body2 = response2.json()
    data2 = body2["data"]

    assert data2["total"] == 10
    assert len(data2["items"]) == 5


# =========================================================
# LIKE-поиск: поиск категорий с родительскими категориями
# =========================================================

@pytest.mark.asyncio
async def test_category_search_with_parent(authorized_client, client):
    """Поиск дочерних категорий"""
    # Создаём родительскую категорию
    parent_resp = await _create_category(authorized_client, "Parent Electronics")
    parent_id = parent_resp.json()["data"]["id"]

    # Создаём дочерние категории
    await _create_category(authorized_client, "Child Phones", parent_id=parent_id)
    await _create_category(authorized_client, "Child Tablets", parent_id=parent_id)

    response = await client.get("/category?name=Child")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    
    # Проверяем, что у найденных категорий есть родитель
    for item in data["items"]:
        assert item["parent"] is not None
        assert item["parent"]["id"] == parent_id


# =========================================================
# LIKE-поиск: поиск с учётом вложенности
# =========================================================

@pytest.mark.asyncio
async def test_category_search_nested_categories(authorized_client, client):
    """Поиск по вложенным категориям"""
    # Создаём иерархию: Электроника -> Телефоны -> Смартфоны
    level1 = await _create_category(authorized_client, "Electronics")
    level2 = await _create_category(authorized_client, "Phones", parent_id=level1.json()["data"]["id"])
    await _create_category(authorized_client, "Smartphones", parent_id=level2.json()["data"]["id"])

    # Ищем по "Phone" - находим "Phones" и "Smartphones" (оба содержат "Phone")
    response = await client.get("/category?name=Phone")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "Phones" in names
    assert "Smartphones" in names
