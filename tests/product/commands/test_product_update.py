import json

import pytest

from src.catalog.product.api.schemas.schemas import ProductReadSchema

JPEG_BYTES = b"\xff\xd8\xff\xe0product-old"
JPEG_BYTES_NEW = b"\xff\xd8\xff\xe0product-new"
JPEG_BYTES_ANOTHER = b"\xff\xd8\xff\xe0product-another"


@pytest.mark.asyncio
async def test_update_product_200_with_image_operations(authorized_client):
    """Обновление товара с использованием операций с изображениями."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар для теста",
            "description": "Описание",
            "price": "100.00",
            "image_is_main": ["true", "false"],
        },
        files=[
            ("images", ("img1.jpg", JPEG_BYTES, "image/jpeg")),
            ("images", ("img2.jpg", JPEG_BYTES_ANOTHER, "image/jpeg")),
        ],
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]
    images = create.json()["data"]["images"]
    assert len(images) == 2
    
    image_1_id = images[0]["image_id"]
    image_2_id = images[1]["image_id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Обновлённый товар",
            "price": "150.00",
            "images_json": json.dumps([
                {"action": "pass", "image_id": image_1_id, "is_main": True},
                {"action": "to_delete", "image_id": image_2_id},
                {"action": "to_create", "is_main": False},
            ]),
        },
        files=[("images", ("new.jpg", JPEG_BYTES_NEW, "image/jpeg"))],
    )

    assert response.status_code == 200

    body = response.json()
    updated = ProductReadSchema(**body["data"])

    assert updated.id == product_id
    assert updated.name == "Обновлённый товар"
    assert str(updated.price) == "150.00"
    assert len(updated.images) == 2


@pytest.mark.asyncio
async def test_update_product_200_pass_all_images(authorized_client):
    """Сохранение всех существующих изображений через pass."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
        files=[
            ("images", ("img1.jpg", JPEG_BYTES, "image/jpeg")),
            ("images", ("img2.jpg", JPEG_BYTES_ANOTHER, "image/jpeg")),
        ],
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]
    images = create.json()["data"]["images"]
    
    images_json = json.dumps([
        {"action": "pass", "image_id": img["image_id"], "is_main": (idx == 0)}
        for idx, img in enumerate(images)
    ])

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Товар обновлён",
            "images_json": images_json,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["images"]) == 2


@pytest.mark.asyncio
async def test_update_product_200_delete_all_images(authorized_client):
    """Удаление всех изображений."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
        files=[
            ("images", ("img1.jpg", JPEG_BYTES, "image/jpeg")),
        ],
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]
    images = create.json()["data"]["images"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Товар без фото",
            "images_json": json.dumps([
                {"action": "to_delete", "image_id": images[0]["image_id"]},
            ]),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["images"]) == 0


@pytest.mark.asyncio
async def test_update_product_200_add_multiple_images(authorized_client):
    """Добавление нескольких новых изображений."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Товар с новыми фото",
            "images_json": json.dumps([
                {"action": "to_create", "is_main": True},
                {"action": "to_create", "is_main": False},
                {"action": "to_create", "is_main": False},
            ]),
        },
        files=[
            ("images", ("new1.jpg", JPEG_BYTES, "image/jpeg")),
            ("images", ("new2.jpg", JPEG_BYTES_NEW, "image/jpeg")),
            ("images", ("new3.jpg", JPEG_BYTES_ANOTHER, "image/jpeg")),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["images"]) == 3


@pytest.mark.asyncio
async def test_update_product_200_mixed_operations(authorized_client):
    """Смешанные операции: pass, to_delete, to_create."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
        files=[
            ("images", ("old1.jpg", JPEG_BYTES, "image/jpeg")),
            ("images", ("old2.jpg", JPEG_BYTES_ANOTHER, "image/jpeg")),
        ],
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]
    images = create.json()["data"]["images"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Товар микс",
            "images_json": json.dumps([
                {"action": "pass", "image_id": images[0]["image_id"], "is_main": True},
                {"action": "to_delete", "image_id": images[1]["image_id"]},
                {"action": "to_create", "is_main": False},
                {"action": "to_create", "is_main": False},
            ]),
        },
        files=[
            ("images", ("new1.jpg", JPEG_BYTES_NEW, "image/jpeg")),
            ("images", ("new2.jpg", JPEG_BYTES_ANOTHER, "image/jpeg")),
        ],
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["images"]) == 3


@pytest.mark.asyncio
async def test_update_product_200_no_images_param(authorized_client):
    """Обновление без параметра images_json - изображения не меняются."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
        files=[
            ("images", ("img1.jpg", JPEG_BYTES, "image/jpeg")),
        ],
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Товар обновлён",
            "price": "200.00",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["images"]) == 1


@pytest.mark.asyncio
async def test_update_product_400_invalid_images_json(authorized_client):
    """Ошибка при невалидном images_json."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Товар",
            "images_json": "not a json",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_invalid_payload"


@pytest.mark.asyncio
async def test_update_product_400_invalid_action(authorized_client):
    """Ошибка при неверном действии в images_json."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Товар",
            "images_json": json.dumps([
                {"action": "invalid_action", "image_id": 1},
            ]),
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_invalid_payload"


@pytest.mark.asyncio
async def test_update_product_404_not_found(authorized_client):
    response = await authorized_client.put(
        "/product/999999",
        data={
            "name": "Not found",
            "price": "1.00",
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_not_found"


@pytest.mark.asyncio
async def test_update_product_200_partial_fields(authorized_client):
    """Обновление только цены без изменения изображений."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
        files=[("images", ("img.jpg", JPEG_BYTES, "image/jpeg"))],
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "price": "250.00",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert str(body["data"]["price"]) == "250.00"
    assert len(body["data"]["images"]) == 1


@pytest.mark.asyncio
async def test_update_product_200_pass_with_image_url(authorized_client):
    """Сохранение изображения через image_key вместо image_id."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
        files=[("images", ("img.jpg", JPEG_BYTES, "image/jpeg"))],
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]
    image_key = create.json()["data"]["images"][0]["image_key"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Обновлённый товар",
            "images_json": json.dumps([
                {"action": "pass", "image_url": image_key, "is_main": True},
                {"action": "to_create", "is_main": False},
            ]),
        },
        files=[("images", ("new.jpg", JPEG_BYTES_NEW, "image/jpeg"))],
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["images"]) == 2


@pytest.mark.asyncio
async def test_update_product_200_pass_without_id_or_url(authorized_client):
    """pass без image_id и image_url сохраняет все существующие изображения."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
        files=[
            ("images", ("img1.jpg", JPEG_BYTES, "image/jpeg")),
            ("images", ("img2.jpg", JPEG_BYTES_ANOTHER, "image/jpeg")),
        ],
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Обновлённый товар",
            "images_json": json.dumps([
                {"action": "pass", "is_main": True},
            ]),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["images"]) == 2
