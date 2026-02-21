import json

import pytest

from src.catalog.product.api.schemas.schemas import ProductReadSchema

JPEG_BYTES = b"\xff\xd8\xff\xe0product-old"
JPEG_BYTES_NEW = b"\xff\xd8\xff\xe0product-new"


@pytest.mark.asyncio
async def test_update_product_200_full_update(authorized_client):
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Старый товар",
            "description": "Старое описание",
            "price": "100.00",
            "attributes_json": json.dumps(
                [
                    {"name": "Цвет", "value": "Красный", "is_filterable": True},
                ]
            ),
        },
        files=[("images", ("old.jpg", JPEG_BYTES, "image/jpeg"))],
    )

    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/product/{product_id}",
        data={
            "name": "Новый товар",
            "description": "Новое описание",
            "price": "150.00",
            "attributes_json": json.dumps(
                [
                    {"name": "Цвет", "value": "Черный", "is_filterable": True},
                    {"name": "Память", "value": "512 Гб", "is_filterable": True},
                ]
            ),
            "image_is_main": "true",
        },
        files=[("images", ("new.jpg", JPEG_BYTES_NEW, "image/jpeg"))],
    )

    assert response.status_code == 200

    body = response.json()
    updated = ProductReadSchema(**body["data"])

    assert updated.id == product_id
    assert updated.name == "Новый товар"
    assert str(updated.price) == "150.00"
    assert len(updated.images) == 1
    assert len(updated.attributes) == 2


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
