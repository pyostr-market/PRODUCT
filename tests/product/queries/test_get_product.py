import json

import pytest

from src.catalog.product.api.schemas.schemas import ProductReadSchema

JPEG_BYTES = b"\xff\xd8\xff\xe0test-image"


@pytest.mark.asyncio
async def test_get_product_200(authorized_client, client):
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар для получения",
            "price": "777.77",
        },
    )
    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await client.get(f"/product/{product_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert product.id == product_id
    assert product.name == "Товар для получения"
    
    # Проверяем, что связанные данные возвращаются (даже если null)
    assert "category" in body["data"]
    assert "supplier" in body["data"]
    assert "product_type" in body["data"]


@pytest.mark.asyncio
async def test_get_product_200_with_category_and_supplier(authorized_client, client):
    """Проверка получения товара с связанными category и supplier."""
    # Создаём категорию
    cat_resp = await authorized_client.post(
        "/category",
        data={"name": "Test Category", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert cat_resp.status_code == 200, f"Category create failed: {cat_resp.json()}"
    category_id = cat_resp.json()["data"]["id"]
    
    # Создаём товар с категорией
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар с категорией",
            "price": "999.99",
            "category_id": str(category_id),
        },
    )
    assert create.status_code == 200, f"Product create failed: {create.json()}"
    product_id = create.json()["data"]["id"]

    response = await client.get(f"/product/{product_id}")

    assert response.status_code == 200
    body = response.json()
    
    # Проверяем, что категория вернулась как вложенный объект
    assert body["data"]["category"] is not None
    assert body["data"]["category"]["id"] == category_id
    assert body["data"]["category"]["name"] == "Test Category"
    
    # supplier и product_type должны быть null
    assert body["data"]["supplier"] is None
    assert body["data"]["product_type"] is None


@pytest.mark.asyncio
async def test_get_product_200_with_images(authorized_client, client, image_storage_mock):
    """Получение товара с изображениями и проверкой ordering."""
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

    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар с изображениями",
            "price": "999.99",
            "images_json": json.dumps([
                {"upload_id": upload_ids[0], "is_main": True, "ordering": 0},
                {"upload_id": upload_ids[1], "is_main": False, "ordering": 1},
            ]),
        },
    )
    assert create.status_code == 200

    product_id = create.json()["data"]["id"]

    response = await client.get(f"/product/{product_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert product.id == product_id
    assert len(product.images) == 2
    # Сортируем изображения по ordering для проверки
    images_sorted = sorted(product.images, key=lambda x: x.ordering)
    assert images_sorted[0].ordering == 0
    assert images_sorted[1].ordering == 1
    assert images_sorted[0].is_main is True


@pytest.mark.asyncio
async def test_get_product_404(client):
    response = await client.get("/product/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_not_found"
