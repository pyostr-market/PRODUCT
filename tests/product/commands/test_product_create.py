import json

import pytest

from src.catalog.product.api.schemas.schemas import ProductReadSchema

JPEG_BYTES = b"\xff\xd8\xff\xe0product-image"


@pytest.mark.asyncio
async def test_create_product_200(authorized_client, image_storage_mock):
    """Создание товара с изображениями через images_json."""
    # Сначала загружаем изображение
    upload_resp = await authorized_client.post(
        "/upload/",
        data={"folder": "products"},
        files=[("file", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert upload_resp.status_code == 200
    upload_id = upload_resp.json()["data"]["upload_id"]

    images_payload = [
        {"upload_id": upload_id, "is_main": True, "ordering": 0}
    ]

    response = await authorized_client.post(
        "/product",
        data={
            "name": "iPhone 15 Pro 256 Гб Красный",
            "description": "Смартфон",
            "price": "129990.00",
            "attributes_json": json.dumps(
                [
                    {"name": "Память", "value": "256 Гб", "is_filterable": True},
                    {"name": "Цвет", "value": "Красный", "is_filterable": True},
                ]
            ),
            "images_json": json.dumps(images_payload),
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert isinstance(product.id, int)
    assert product.name == "iPhone 15 Pro 256 Гб Красный"
    assert len(product.images) == 1
    assert product.images[0].is_main is True
    assert product.images[0].ordering == 0
    assert len(product.attributes) == 2
    assert product.images[0].upload_id == upload_id


@pytest.mark.asyncio
async def test_create_product_200_multiple_images(authorized_client, image_storage_mock):
    """Создание товара с несколькими изображениями через images_json."""
    # Загружаем несколько изображений
    upload_ids = []
    for i in range(3):
        upload_resp = await authorized_client.post(
            "/upload/",
            data={"folder": "products"},
            files=[("file", (f"test{i}.jpg", JPEG_BYTES, "image/jpeg"))],
        )
        assert upload_resp.status_code == 200
        upload_ids.append(upload_resp.json()["data"]["upload_id"])

    images_payload = [
        {"upload_id": upload_ids[0], "is_main": True, "ordering": 0},
        {"upload_id": upload_ids[1], "is_main": False, "ordering": 1},
        {"upload_id": upload_ids[2], "is_main": False, "ordering": 2},
    ]

    response = await authorized_client.post(
        "/product",
        data={
            "name": "Товар с несколькими фото",
            "price": "100.00",
            "images_json": json.dumps(images_payload),
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert len(product.images) == 3
    assert product.images[0].is_main is True
    assert product.images[0].ordering == 0
    assert product.images[1].ordering == 1
    assert product.images[2].ordering == 2
    assert all(img.upload_id in upload_ids for img in product.images)


@pytest.mark.asyncio
async def test_create_product_200_no_images(authorized_client):
    """Создание товара без изображений."""
    response = await authorized_client.post(
        "/product",
        data={
            "name": "Товар без фото",
            "price": "100.00",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert len(product.images) == 0


@pytest.mark.asyncio
async def test_create_product_200_custom_ordering(authorized_client, image_storage_mock):
    """Создание товара с изображениями с кастомным порядком через images_json."""
    # Загружаем несколько изображений
    upload_ids = []
    for i in range(3):
        upload_resp = await authorized_client.post(
            "/upload/",
            data={"folder": "products"},
            files=[("file", (f"test{i}.jpg", JPEG_BYTES, "image/jpeg"))],
        )
        assert upload_resp.status_code == 200
        upload_ids.append(upload_resp.json()["data"]["upload_id"])

    images_payload = [
        {"upload_id": upload_ids[0], "is_main": False, "ordering": 10},
        {"upload_id": upload_ids[1], "is_main": True, "ordering": 5},
        {"upload_id": upload_ids[2], "is_main": False, "ordering": 20},
    ]

    response = await authorized_client.post(
        "/product",
        data={
            "name": "Товар с кастомным порядком",
            "price": "100.00",
            "images_json": json.dumps(images_payload),
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert len(product.images) == 3

    # Проверяем, что ordering сохранился как указан
    orderings = {img.ordering: img for img in product.images}
    assert 5 in orderings
    assert 10 in orderings
    assert 20 in orderings
    assert orderings[5].is_main is True  # Главное изображение с ordering=5


@pytest.mark.asyncio
async def test_create_product_400_name_too_short(authorized_client):
    """Создание товара с слишком коротким именем."""
    response = await authorized_client.post(
        "/product",
        data={
            "name": "A",
            "price": "999.99",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_name_too_short"


@pytest.mark.asyncio
async def test_create_product_400_missing_upload_id(authorized_client):
    """Создание товара с отсутствующим upload_id."""
    images_payload = [
        {"is_main": True, "ordering": 0},
    ]

    response = await authorized_client.post(
        "/product",
        data={
            "name": "Некорректный товар",
            "price": "10.00",
            "images_json": json.dumps(images_payload),
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_invalid_payload"


@pytest.mark.asyncio
async def test_create_product_400_invalid_images_json(authorized_client):
    """Создание товара с некорректным images_json."""
    response = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "10.00",
            "images_json": "not valid json",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_invalid_payload"


@pytest.mark.asyncio
async def test_create_product_400_images_must_be_list(authorized_client):
    """Создание товара с images_json не как список."""
    response = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "10.00",
            "images_json": json.dumps({"upload_id": 1}),
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_invalid_payload"


@pytest.mark.asyncio
async def test_create_product_200_with_category(authorized_client, image_storage_mock):
    """Создание товара с категорией через images_json."""
    # Сначала создаём категорию
    cat_resp = await authorized_client.post(
        "/category",
        data={"name": "Test Category", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert cat_resp.status_code == 200
    category_id = cat_resp.json()["data"]["id"]

    # Загружаем изображение
    upload_resp = await authorized_client.post(
        "/upload/",
        data={"folder": "products"},
        files=[("file", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert upload_resp.status_code == 200
    upload_id = upload_resp.json()["data"]["upload_id"]

    images_payload = [
        {"upload_id": upload_id, "is_main": True, "ordering": 0},
    ]

    response = await authorized_client.post(
        "/product",
        data={
            "name": "Товар с категорией",
            "price": "999.00",
            "category_id": str(category_id),
            "images_json": json.dumps(images_payload),
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert product.category_id == category_id
    assert len(product.images) == 1
    assert product.images[0].upload_id == upload_id
