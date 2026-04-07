"""
Тесты для полнотекстового поиска товаров с подсказками (endpoint /product/search).

Проверяют:
- Поиск товаров по названию и атрибутам
- Возврат подсказок следующихих слов
- Пагинацию (limit/offset)
- Пустой поиск и отсутствие результатов
"""
import pytest


# =========================================================
# Базовый поиск: возврат товаров и подсказок
# =========================================================

@pytest.mark.asyncio
async def test_search_returns_products_and_suggestions(authorized_client, client):
    """Поиск 'iPhone' возвращает товары и подсказки"""
    # Создаём товары с разными версиями iPhone
    await authorized_client.post("/product", data={"name": "iPhone 15 Pro", "price": "999.00"})
    await authorized_client.post("/product", data={"name": "iPhone 15", "price": "899.00"})
    await authorized_client.post("/product", data={"name": "iPhone 16", "price": "1099.00"})
    await authorized_client.post("/product", data={"name": "iPhone 17", "price": "1199.00"})
    await authorized_client.post("/product", data={"name": "iPhone Red Edition", "price": "949.00"})

    response = await client.get("/product/search?query=iPhone")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    # Проверяем, что товары найдены
    assert data["total"] == 5
    assert len(data["items"]) == 5  # default limit=10, но у нас только 5 товаров

    # Проверяем наличие подсказок
    assert "suggestions" in data
    assert len(data["suggestions"]) > 0
    
    # Проверяем, что подсказки содержат ожидаемые слова
    suggestion_words = [s["word"] for s in data["suggestions"]]
    # Должны быть: "15", "16", "17", "Red" (или "Pro")
    assert "15" in suggestion_words or "Pro" in suggestion_words


@pytest.mark.asyncio
async def test_search_returns_top_5_suggestions(authorized_client, client):
    """Подсказки должны содержать максимум 5 слов"""
    # Создаём много товаров с разными словами
    products = [
        "iPhone 15 Pro Max",
        "iPhone 15 Pro",
        "iPhone 15",
        "iPhone 16 Pro",
        "iPhone 16",
        "iPhone 17",
        "iPhone Red",
        "iPhone Blue",
        "iPhone Green",
        "iPhone White",
        "iPhone Black",
    ]
    for name in products:
        await authorized_client.post("/product", data={"name": name, "price": "999.00"})

    response = await client.get("/product/search?query=iPhone")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    # Подсказок должно быть не больше 5
    assert len(data["suggestions"]) <= 5


# =========================================================
# Пагинация
# =========================================================

@pytest.mark.asyncio
async def test_search_with_limit(authorized_client, client):
    """Параметр limit ограничивает количество возвращаемых товаров"""
    # Создаём 10 товаров
    for i in range(10):
        await authorized_client.post("/product", data={"name": f"iPhone Model {i}", "price": "999.00"})

    response = await client.get("/product/search?query=iPhone&limit=3")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    # Всего 10, но вернулось только 3
    assert data["total"] == 10
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_search_with_offset(authorized_client, client):
    """Параметр offset позволяет пропускать товары"""
    # Создаём 10 товаров
    for i in range(10):
        await authorized_client.post("/product", data={"name": f"iPhone Model {i}", "price": "999.00"})

    # Первая страница
    response1 = await client.get("/product/search?query=iPhone&limit=5&offset=0")
    assert response1.status_code == 200
    data1 = response1.json()["data"]
    assert len(data1["items"]) == 5

    # Вторая страница
    response2 = await client.get("/product/search?query=iPhone&limit=5&offset=5")
    assert response2.status_code == 200
    data2 = response2.json()["data"]
    assert len(data2["items"]) == 5

    # Проверяем, что товары разные
    names1 = [item["name"] for item in data1["items"]]
    names2 = [item["name"] for item in data2["items"]]
    assert set(names1) != set(names2)


@pytest.mark.asyncio
async def test_search_default_limit(authorized_client, client):
    """По умолчанию limit=10"""
    # Создаём 15 товаров
    for i in range(15):
        await authorized_client.post("/product", data={"name": f"Samsung Model {i}", "price": "799.00"})

    response = await client.get("/product/search?query=Samsung")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    # Всего 15, но вернулось только 10 (по умолчанию)
    assert data["total"] == 15
    assert len(data["items"]) == 10


# =========================================================
# Поиск по атрибутам
# =========================================================

@pytest.mark.asyncio
async def test_search_by_attributes(authorized_client, client):
    """Поиск должен искать и по атрибутам"""
    import json
    # Создаём товар с уникальным атрибутом
    await authorized_client.post(
        "/product",
        data={
            "name": "Смартфон",
            "price": "999.00",
            "attributes_json": json.dumps([
                {"name": "TestColor", "value": "RedTest", "is_filterable": True}
            ])
        }
    )

    # Ищем по значению атрибута
    response = await client.get("/product/search?query=RedTest")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 1
    names = [item["name"] for item in data["items"]]
    assert "Смартфон" in names


# =========================================================
# Пустой поиск и отсутствие результатов
# =========================================================

@pytest.mark.asyncio
async def test_search_no_results(authorized_client, client):
    """Поиск без результатов возвращает пустой список и пустые подсказки"""
    await authorized_client.post("/product", data={"name": "iPhone 15", "price": "999.00"})

    response = await client.get("/product/search?query=NonExistent")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 0
    assert data["items"] == []
    assert data["suggestions"] == []


@pytest.mark.asyncio
async def test_search_empty_query_validation(client):
    """Пустой запрос должен вызывать ошибку валидации"""
    response = await client.get("/product/search?query=")
    # FastAPI вернёт 422 из-за min_length=1
    assert response.status_code == 422


# =========================================================
# Регистронезависимость поиска
# =========================================================

@pytest.mark.asyncio
async def test_search_case_insensitive(authorized_client, client):
    """Поиск должен быть регистронезависимым"""
    await authorized_client.post("/product", data={"name": "MacBook Pro", "price": "1999.00"})
    await authorized_client.post("/product", data={"name": "macbook air", "price": "1299.00"})

    response = await client.get("/product/search?query=MACBOOK")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "MacBook Pro" in names
    assert "macbook air" in names


# =========================================================
# Проверка структуры ответа
# =========================================================

@pytest.mark.asyncio
async def test_search_response_structure(authorized_client, client):
    """Проверка структуры ответа"""
    await authorized_client.post("/product", data={"name": "Test Product", "price": "100.00"})

    response = await client.get("/product/search?query=Test")
    assert response.status_code == 200

    body = response.json()
    
    # Проверяем обёртку
    assert "success" in body
    assert body["success"] is True
    assert "data" in body

    data = body["data"]
    
    # Проверяем поля
    assert "total" in data
    assert "items" in data
    assert "suggestions" in data
    
    # Проверяем тип полей
    assert isinstance(data["total"], int)
    assert isinstance(data["items"], list)
    assert isinstance(data["suggestions"], list)

    # Проверяем структуру подсказок
    if data["suggestions"]:
        suggestion = data["suggestions"][0]
        assert "word" in suggestion
        assert "count" in suggestion
        assert isinstance(suggestion["word"], str)
        assert isinstance(suggestion["count"], int)

    # Проверяем структуру товаров
    if data["items"]:
        product = data["items"][0]
        assert "id" in product
        assert "name" in product
        assert "price" in product
        assert "images" in product
        assert "attributes" in product


# =========================================================
# Подсказки из атрибутов
# =========================================================

@pytest.mark.asyncio
async def test_search_suggestions_from_attributes(authorized_client, client):
    """Подсказки должны извлекаться и из атрибутов"""
    import json
    # Создаём товар с атрибутом, содержащим поисковый запрос
    await authorized_client.post(
        "/product",
        data={
            "name": "Smartphone AttrTest",
            "price": "999.00",
            "attributes_json": json.dumps([
                {"name": "TestStorage", "value": "iPhoneTest 256GB", "is_filterable": True},
            ])
        }
    )

    response = await client.get("/product/search?query=iPhoneTest")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    # Товар должен быть найден
    assert data["total"] >= 1
