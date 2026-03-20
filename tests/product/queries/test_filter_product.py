import json

import pytest


@pytest.mark.asyncio
async def test_filter_products_by_sort_type_price_asc(authorized_client, client):
    """
    Проверяет сортировку товаров по цене (возрастание).

    Сценарий:
    1. Создаём 3 товара с разной ценой
    2. Запрашиваем товары с sort_type=price_asc
    3. Проверяем, что товары отсортированы по возрастанию цены
    """
    # Создаём товары с разной ценой
    await authorized_client.post("/product", data={"name": "Product Cheap", "price": "100.00"})
    await authorized_client.post("/product", data={"name": "Product Medium", "price": "500.00"})
    await authorized_client.post("/product", data={"name": "Product Expensive", "price": "1000.00"})

    response = await client.get("/product?sort_type=price_asc&limit=10")

    assert response.status_code == 200
    body = response.json()
    data = body["data"]

    assert data["total"] >= 3
    items = data["items"]

    # Проверяем порядок сортировки по возрастанию цены
    prices = [float(item["price"]) for item in items]
    assert prices == sorted(prices), f"Ожидалась сортировка по возрастанию, но получено: {prices}"


@pytest.mark.asyncio
async def test_filter_products_by_sort_type_price_desc(authorized_client, client):
    """
    Проверяет сортировку товаров по цене (убывание).

    Сценарий:
    1. Создаём 3 товара с разной ценой
    2. Запрашиваем товары с sort_type=price_desc
    3. Проверяем, что товары отсортированы по убыванию цены
    """
    # Создаём товары с разной ценой
    await authorized_client.post("/product", data={"name": "Product Cheap", "price": "100.00"})
    await authorized_client.post("/product", data={"name": "Product Medium", "price": "500.00"})
    await authorized_client.post("/product", data={"name": "Product Expensive", "price": "1000.00"})

    response = await client.get("/product?sort_type=price_desc&limit=10")

    assert response.status_code == 200
    body = response.json()
    data = body["data"]

    assert data["total"] >= 3
    items = data["items"]

    # Проверяем порядок сортировки по убыванию цены
    prices = [float(item["price"]) for item in items]
    assert prices == sorted(prices, reverse=True), f"Ожидалась сортировка по убыванию, но получено: {prices}"


@pytest.mark.asyncio
async def test_filter_products_by_sort_type_default(authorized_client, client):
    """
    Проверяет сортировку товаров по умолчанию (по ID).

    Сценарий:
    1. Создаём 3 товара
    2. Запрашиваем товары с sort_type=default
    3. Проверяем, что товары отсортированы по ID
    """
    # Создаём товары
    resp1 = await authorized_client.post("/product", data={"name": "Product First", "price": "500.00"})
    resp2 = await authorized_client.post("/product", data={"name": "Product Second", "price": "100.00"})
    resp3 = await authorized_client.post("/product", data={"name": "Product Third", "price": "1000.00"})

    response = await client.get("/product?sort_type=default&limit=10")

    assert response.status_code == 200
    body = response.json()
    data = body["data"]

    assert data["total"] >= 3
    items = data["items"]

    # Проверяем, что ID отсортированы по возрастанию
    ids = [item["id"] for item in items]
    assert ids == sorted(ids), f"Ожидалась сортировка по ID, но получено: {ids}"


@pytest.mark.asyncio
async def test_filter_products_with_sort_and_attributes(authorized_client, client):
    """
    Проверяет комбинацию фильтрации по атрибутам с сортировкой.

    Сценарий:
    1. Создаём категорию и товары с атрибутами
    2. Запрашиваем товары с фильтрацией по атрибутам и сортировкой
    3. Проверяем, что фильтрация и сортировка работают вместе
    """
    # Создаём категорию
    cat_resp = await authorized_client.post("/category", json={"name": "Test Category"})
    category_id = cat_resp.json()["data"]["id"]

    # Создаём товары с разными атрибутами и ценами
    await authorized_client.post(
        "/product",
        data={
            "name": "Product RAM 8GB",
            "price": "500.00",
            "category_id": str(category_id),
            "attributes_json": json.dumps([{"name": "RAM", "value": "8 GB", "is_filterable": True}]),
        },
    )
    await authorized_client.post(
        "/product",
        data={
            "name": "Product RAM 16GB Cheap",
            "price": "300.00",
            "category_id": str(category_id),
            "attributes_json": json.dumps([{"name": "RAM", "value": "16 GB", "is_filterable": True}]),
        },
    )
    await authorized_client.post(
        "/product",
        data={
            "name": "Product RAM 16GB Expensive",
            "price": "800.00",
            "category_id": str(category_id),
            "attributes_json": json.dumps([{"name": "RAM", "value": "16 GB", "is_filterable": True}]),
        },
    )

    # Фильтруем по RAM=16GB и сортируем по возрастанию цены
    response = await client.get(
        f"/product?category_id={category_id}&attributes={{\"RAM\":[\"16 GB\"]}}&sort_type=price_asc"
    )

    assert response.status_code == 200
    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    items = data["items"]

    # Проверяем, что все товары имеют RAM 16GB
    for item in items:
        ram_attr = next((attr for attr in item["attributes"] if attr["name"] == "RAM"), None)
        assert ram_attr is not None
        assert ram_attr["value"] == "16 GB"

    # Проверяем сортировку по возрастанию цены
    prices = [float(item["price"]) for item in items]
    assert prices == sorted(prices), f"Ожидалась сортировка по возрастанию, но получено: {prices}"


@pytest.mark.asyncio
async def test_filter_product_list_200(authorized_client, client):
    names = ["Product A", "Product B", "Product C"]

    for name in names:
        r = await authorized_client.post(
            "/product",
            data={
                "name": name,
                "price": "100.00",
            },
        )
        assert r.status_code == 200

    response = await client.get("/product")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 3
    assert len(data["items"]) >= 3

    # Проверяем, что у товаров есть изображения с ordering и связанные данные
    for item in data["items"]:
        assert "images" in item
        for image in item["images"]:
            assert "ordering" in image
        # Проверяем наличие связанных данных (могут быть null)
        assert "category" in item
        assert "supplier" in item


@pytest.mark.asyncio
async def test_filter_product_by_name(authorized_client, client):
    await authorized_client.post("/product", data={"name": "Filter iPhone", "price": "1.00"})
    await authorized_client.post("/product", data={"name": "Filter Samsung", "price": "1.00"})
    await authorized_client.post("/product", data={"name": "Other Item", "price": "1.00"})

    response = await client.get("/product?name=Filter")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]

    assert "Filter iPhone" in names
    assert "Filter Samsung" in names
    assert "Other Item" not in names


@pytest.mark.asyncio
async def test_filter_product_with_category(authorized_client, client):
    """Фильтрация товаров с проверкой связанных категорий."""
    # Создаём категорию
    cat_resp = await authorized_client.post(
        "/category",
        json={"name": "Filter Category"},
    )
    assert cat_resp.status_code == 200, f"Category create failed: {cat_resp.json()}"
    category_id = cat_resp.json()["data"]["id"]
    
    # Создаём товар с категорией
    await authorized_client.post(
        "/product",
        data={
            "name": "Product with Category",
            "price": "999.00",
            "category_id": str(category_id),
        },
    )

    response = await client.get("/product?name=Product")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 1
    product = data["items"][0]

    # Проверяем, что категория вернулась как вложенный объект
    assert product["category"] is not None
    assert product["category"]["id"] == category_id
    assert product["category"]["name"] == "Filter Category"


@pytest.mark.asyncio
async def test_filter_product_with_images_and_ordering(authorized_client, client, image_storage_mock):
    """Фильтрация товаров с изображениями и проверкой ordering."""
    # Загружаем изображения
    upload_ids = []
    for i in range(2):
        upload_resp = await authorized_client.post(
            "/upload/",
            data={"folder": "products"},
            files=[("file", (f"img{i}.jpg", b"\xff\xd8\xff\xe0test{i}", "image/jpeg"))],
        )
        assert upload_resp.status_code == 200
        upload_ids.append(upload_resp.json()["data"]["upload_id"])

    await authorized_client.post(
        "/product",
        data={
            "name": "Product with images",
            "price": "999.00",
            "images_json": json.dumps([
                {"upload_id": upload_ids[0], "is_main": True, "ordering": 0},
                {"upload_id": upload_ids[1], "is_main": False, "ordering": 1},
            ]),
        },
    )

    response = await client.get("/product?name=Product")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 1
    product = data["items"][0]

    assert len(product["images"]) == 2
    # Сортируем изображения по ordering для проверки
    images_sorted = sorted(product["images"], key=lambda x: x["ordering"])
    assert images_sorted[0]["ordering"] == 0
    assert images_sorted[1]["ordering"] == 1
    assert images_sorted[0]["is_main"] is True
