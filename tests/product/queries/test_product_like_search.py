"""
Тесты для LIKE-поиска по товарам (product).

Проверяют поиск по полю name с использованием различных сценариев:
- Поиск по части слова (ilike)
- Регистронезависимый поиск
- Поиск с специальными символами
- Поиск по началу/концу/середине слова
- Комбинация с фильтрами category_id, product_type_id
"""
import pytest

JPEG_BYTES = b"\xff\xd8\xff\xe0test-image"


# =========================================================
# LIKE-поиск: регистронезависимость
# =========================================================

@pytest.mark.asyncio
async def test_product_search_case_insensitive_upper(authorized_client, client):
    """Поиск 'IPHONE' должен найти 'iPhone'"""
    await authorized_client.post("/product", data={"name": "iPhone", "price": "999.00"})
    await authorized_client.post("/product", data={"name": "Samsung Galaxy", "price": "899.00"})

    response = await client.get("/product?name=IPHONE")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "iPhone"


@pytest.mark.asyncio
async def test_product_search_case_insensitive_lower(authorized_client, client):
    """Поиск 'galaxy' должен найти 'Galaxy'"""
    await authorized_client.post("/product", data={"name": "iPhone", "price": "999.00"})
    await authorized_client.post("/product", data={"name": "Galaxy S23", "price": "899.00"})

    response = await client.get("/product?name=galaxy")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Galaxy S23"


@pytest.mark.asyncio
async def test_product_search_case_insensitive_mixed(authorized_client, client):
    """Поиск 'MacBoOk' должен найти 'MacBook'"""
    await authorized_client.post("/product", data={"name": "MacBook Pro", "price": "1999.00"})

    response = await client.get("/product?name=MacBoOk")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "MacBook Pro"


# =========================================================
# LIKE-поиск: поиск по части слова
# =========================================================

@pytest.mark.asyncio
async def test_product_search_by_startswith(authorized_client, client):
    """Поиск по началу слова: 'iPh' находит 'iPhone'"""
    await authorized_client.post("/product", data={"name": "iPhone 15", "price": "999.00"})
    await authorized_client.post("/product", data={"name": "iPhone 14", "price": "899.00"})
    await authorized_client.post("/product", data={"name": "Samsung Galaxy", "price": "799.00"})

    response = await client.get("/product?name=iPh")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "iPhone 15" in names
    assert "iPhone 14" in names
    assert "Samsung Galaxy" not in names


@pytest.mark.asyncio
async def test_product_search_by_endswith(authorized_client, client):
    """Поиск по концу слова: 'Pro' находит 'MacBook Pro', 'iPhone Pro'"""
    await authorized_client.post("/product", data={"name": "MacBook Pro", "price": "1999.00"})
    await authorized_client.post("/product", data={"name": "iPhone Pro", "price": "1099.00"})
    await authorized_client.post("/product", data={"name": "MacBook Air", "price": "1299.00"})

    response = await client.get("/product?name=Pro")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "MacBook Pro" in names
    assert "iPhone Pro" in names
    assert "MacBook Air" not in names


@pytest.mark.asyncio
async def test_product_search_by_contains(authorized_client, client):
    """Поиск по середине слова: 'ook' находит 'MacBook'"""
    await authorized_client.post("/product", data={"name": "MacBook Pro", "price": "1999.00"})
    await authorized_client.post("/product", data={"name": "Notebook Dell", "price": "1299.00"})
    await authorized_client.post("/product", data={"name": "Desktop HP", "price": "999.00"})

    response = await client.get("/product?name=ook")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "MacBook Pro" in names
    assert "Notebook Dell" in names
    assert "Desktop HP" not in names


# =========================================================
# LIKE-поиск: поиск по полному совпадению
# =========================================================

@pytest.mark.asyncio
async def test_product_search_exact_match(authorized_client, client):
    """Поиск по точному совпадению"""
    await authorized_client.post("/product", data={"name": "Exact Product Name", "price": "100.00"})
    await authorized_client.post("/product", data={"name": "Other Product", "price": "200.00"})

    response = await client.get("/product?name=Exact Product Name")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Exact Product Name"


# =========================================================
# LIKE-поиск: поиск с пробелами и специальными символами
# =========================================================

@pytest.mark.asyncio
async def test_product_search_with_spaces(authorized_client, client):
    """Поиск по названию с пробелами"""
    await authorized_client.post("/product", data={"name": "Apple iPhone 15 Pro Max", "price": "1199.00"})
    await authorized_client.post("/product", data={"name": "Apple iPhone 15", "price": "799.00"})

    response = await client.get("/product?name=Apple iPhone 15 Pro Max")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Apple iPhone 15 Pro Max"


@pytest.mark.asyncio
async def test_product_search_with_hyphen(authorized_client, client):
    """Поиск по названию с дефисом"""
    await authorized_client.post("/product", data={"name": "All-in-One PC", "price": "1499.00"})
    await authorized_client.post("/product", data={"name": "All in One PC", "price": "1399.00"})

    response = await client.get("/product?name=All-in-One")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "All-in-One PC"


@pytest.mark.asyncio
async def test_product_search_with_numbers(authorized_client, client):
    """Поиск по названию с цифрами"""
    await authorized_client.post("/product", data={"name": "iPhone 15", "price": "999.00"})
    await authorized_client.post("/product", data={"name": "iPhone 14", "price": "899.00"})
    await authorized_client.post("/product", data={"name": "iPhone 13", "price": "799.00"})

    response = await client.get("/product?name=15")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "iPhone 15"


# =========================================================
# LIKE-поиск: пустой и специальный поиск
# =========================================================

@pytest.mark.asyncio
async def test_product_search_empty_string(authorized_client, client):
    """Пустой поиск должен вернуть все записи"""
    await authorized_client.post("/product", data={"name": "Product A", "price": "100.00"})
    await authorized_client.post("/product", data={"name": "Product B", "price": "200.00"})

    response = await client.get("/product?name=")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2


@pytest.mark.asyncio
async def test_product_search_no_results(authorized_client, client):
    """Поиск без результатов"""
    await authorized_client.post("/product", data={"name": "Product A", "price": "100.00"})
    await authorized_client.post("/product", data={"name": "Product B", "price": "200.00"})

    response = await client.get("/product?name=NonExistent")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 0
    assert data["items"] == []


# =========================================================
# LIKE-поиск: комбинация с пагинацией
# =========================================================

@pytest.mark.asyncio
async def test_product_search_with_pagination(authorized_client, client):
    """Поиск с пагинацией"""
    for i in range(10):
        await authorized_client.post("/product", data={"name": f"Search Test Product {i}", "price": "100.00"})
    await authorized_client.post("/product", data={"name": "Other Product", "price": "200.00"})

    response = await client.get("/product?name=Search&limit=5&offset=0")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 10
    assert len(data["items"]) == 5

    # Проверяем вторую страницу
    response2 = await client.get("/product?name=Search&limit=5&offset=5")
    assert response2.status_code == 200

    body2 = response2.json()
    data2 = body2["data"]

    assert data2["total"] == 10
    assert len(data2["items"]) == 5


# =========================================================
# LIKE-поиск: комбинация с фильтром по категории
# =========================================================

@pytest.mark.asyncio
async def test_product_search_with_category_filter(authorized_client, client):
    """Поиск товаров с фильтром по категории"""
    # Создаём категории
    cat1_resp = await authorized_client.post(
        "/category",
        data={"name": "Phones", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    cat2_resp = await authorized_client.post(
        "/category",
        data={"name": "Laptops", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    
    cat1_id = cat1_resp.json()["data"]["id"]
    cat2_id = cat2_resp.json()["data"]["id"]

    # Создаём товары
    await authorized_client.post("/product", data={"name": "iPhone", "price": "999.00", "category_id": str(cat1_id)})
    await authorized_client.post("/product", data={"name": "Samsung", "price": "899.00", "category_id": str(cat1_id)})
    await authorized_client.post("/product", data={"name": "MacBook", "price": "1999.00", "category_id": str(cat2_id)})

    # Ищем в категории Phones
    response = await client.get(f"/product?name=&category_id={cat1_id}")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    for item in data["items"]:
        assert item["category"]["id"] == cat1_id


# =========================================================
# LIKE-поиск: комбинация с фильтром по product_type
# =========================================================

@pytest.mark.asyncio
async def test_product_search_with_product_type_filter(authorized_client, client):
    """Поиск товаров с фильтром по product_type"""
    # Создаём типы продуктов
    type1_resp = await authorized_client.post("/product/type", json={"name": "Smartphone", "parent_id": None})
    type2_resp = await authorized_client.post("/product/type", json={"name": "Laptop", "parent_id": None})
    
    type1_id = type1_resp.json()["data"]["id"]
    type2_id = type2_resp.json()["data"]["id"]

    # Создаём товары
    await authorized_client.post("/product", data={"name": "iPhone", "price": "999.00", "product_type_id": str(type1_id)})
    await authorized_client.post("/product", data={"name": "Samsung", "price": "899.00", "product_type_id": str(type1_id)})
    await authorized_client.post("/product", data={"name": "MacBook", "price": "1999.00", "product_type_id": str(type2_id)})

    # Ищем в типе Smartphone
    response = await client.get(f"/product?name=&product_type_id={type1_id}")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    for item in data["items"]:
        assert item["product_type"]["id"] == type1_id


# =========================================================
# LIKE-поиск: комбинация name + category + product_type
# =========================================================

@pytest.mark.asyncio
async def test_product_search_combined_filters(authorized_client, client):
    """Комбинированный поиск: name + category_id + product_type_id"""
    # Создаём категорию и тип
    cat_resp = await authorized_client.post(
        "/category",
        data={"name": "Mobile", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    type_resp = await authorized_client.post("/product/type", json={"name": "Phone", "parent_id": None})
    
    cat_id = cat_resp.json()["data"]["id"]
    type_id = type_resp.json()["data"]["id"]

    # Создаём товары
    await authorized_client.post("/product", data={"name": "iPhone 15", "price": "999.00", "category_id": str(cat_id), "product_type_id": str(type_id)})
    await authorized_client.post("/product", data={"name": "iPhone 14", "price": "899.00", "category_id": str(cat_id), "product_type_id": str(type_id)})
    await authorized_client.post("/product", data={"name": "Samsung Galaxy", "price": "799.00", "category_id": str(cat_id), "product_type_id": str(type_id)})
    await authorized_client.post("/product", data={"name": "MacBook", "price": "1999.00"})

    # Ищем iPhone в категории Mobile
    response = await client.get(f"/product?name=iPhone&category_id={cat_id}")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]
    assert "iPhone 15" in names
    assert "iPhone 14" in names


# =========================================================
# LIKE-поиск: поиск по кириллическим названиям
# =========================================================

@pytest.mark.asyncio
async def test_product_search_cyrillic(authorized_client, client):
    """Поиск по кириллическим названиям"""
    await authorized_client.post("/product", data={"name": "Телефон Xiaomi", "price": "299.00"})
    await authorized_client.post("/product", data={"name": "Ноутбук ASUS", "price": "999.00"})

    response = await client.get("/product?name=Телефон")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Телефон Xiaomi"


@pytest.mark.asyncio
async def test_product_search_cyrillic_case_insensitive(authorized_client, client):
    """Регистронезависимый поиск по кириллице"""
    await authorized_client.post("/product", data={"name": "Смартфон Samsung", "price": "599.00"})

    response = await client.get("/product?name=смартфон")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    assert data["items"][0]["name"] == "Смартфон Samsung"


# =========================================================
# LIKE-поиск: проверка связанных данных в результатах
# =========================================================

@pytest.mark.asyncio
async def test_product_search_returns_related_data(authorized_client, client):
    """Поиск должен возвращать связанные данные (category, supplier, product_type, images, attributes)"""
    # Создаём категорию
    cat_resp = await authorized_client.post(
        "/category",
        data={"name": "Test Category", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    cat_id = cat_resp.json()["data"]["id"]

    # Создаём тип продукта
    type_resp = await authorized_client.post("/product/type", json={"name": "Test Type", "parent_id": None})
    type_id = type_resp.json()["data"]["id"]

    # Создаём товар
    await authorized_client.post(
        "/product",
        data={
            "name": "Test Product Search",
            "price": "100.00",
            "category_id": str(cat_id),
            "product_type_id": str(type_id),
        },
    )

    response = await client.get("/product?name=Test Product")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 1
    product = data["items"][0]

    # Проверяем наличие связанных данных
    assert product["category"] is not None
    assert product["category"]["name"] == "Test Category"
    assert product["product_type"] is not None
    assert product["product_type"]["name"] == "Test Type"
    assert "images" in product
    assert "attributes" in product
