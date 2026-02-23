import base64
import json

import pytest

from src.catalog.product.api.schemas.schemas import ProductReadSchema

JPEG_BYTES = b"\xff\xd8\xff\xe0product-old"
JPEG_BYTES_NEW = b"\xff\xd8\xff\xe0product-new"
JPEG_BYTES_ANOTHER = b"\xff\xd8\xff\xe0product-another"


def _encode_image_base64(image_bytes: bytes) -> str:
    """Кодировать изображение в base64 data URL."""
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{encoded}"


@pytest.mark.asyncio
async def test_update_product_200_basic(authorized_client):
    """Обновление основных полей товара."""
    # Создаём товар
    images_payload = [{"image": _encode_image_base64(JPEG_BYTES), "is_main": True, "ordering": 0}]
    
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар для теста",
            "description": "Описание",
            "price": "100.00",
            "images_json": json.dumps(images_payload),
        },
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Обновлённый товар",
            "price": "150.00",
            "description": "Новое описание",
        },
    )

    assert response.status_code == 200

    body = response.json()
    updated = ProductReadSchema(**body["data"])

    assert updated.id == product_id
    assert updated.name == "Обновлённый товар"
    assert str(updated.price) == "150.00"
    assert updated.description == "Новое описание"


@pytest.mark.asyncio
async def test_update_product_200_delete_image(authorized_client):
    """Удаление изображения товара."""
    images_payload = [
        {"image": _encode_image_base64(JPEG_BYTES), "is_main": True, "ordering": 0},
        {"image": _encode_image_base64(JPEG_BYTES_ANOTHER), "is_main": False, "ordering": 1},
    ]
    
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
            "images_json": json.dumps(images_payload),
        },
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]
    images = create.json()["data"]["images"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Товар без фото",
            "images_json": json.dumps([
                {"action": "delete", "upload_id": images[0]["upload_id"]},
                {"action": "delete", "upload_id": images[1]["upload_id"]},
            ]),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["images"]) == 0


@pytest.mark.asyncio
async def test_update_product_200_add_image(authorized_client):
    """Добавление изображения к товару."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
        },
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    # Сначала загружаем изображение через upload endpoint
    upload_resp = await authorized_client.post(
        "/upload/",
        data={"folder": "products"},
        files=[("file", ("test.jpg", JPEG_BYTES_NEW, "image/jpeg"))],
    )
    assert upload_resp.status_code == 200
    upload_id = upload_resp.json()["data"]["upload_id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Товар с фото",
            "images_json": json.dumps([
                {"action": "create", "upload_id": upload_id, "is_main": True, "ordering": 0},
            ]),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["images"]) == 1
    assert body["data"]["images"][0]["upload_id"] == upload_id


@pytest.mark.asyncio
async def test_update_product_404_not_found(authorized_client):
    """Обновление несуществующего товара."""
    response = await authorized_client.put(
        "/product/999999",
        data={"name": "Товар"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_not_found"


@pytest.mark.asyncio
async def test_update_product_400_name_too_short(authorized_client):
    """Обновление с слишком коротким именем."""
    images_payload = [{"image": _encode_image_base64(JPEG_BYTES), "is_main": True, "ordering": 0}]
    
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар",
            "price": "100.00",
            "images_json": json.dumps(images_payload),
        },
    )
    product_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={"name": "A"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_name_too_short"
