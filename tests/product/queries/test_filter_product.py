import json

import pytest

JPEG_BYTES = b"\xff\xd8\xff\xe0test-image"


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
        assert "product_type" in item


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
        data={"name": "Filter Category", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
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
