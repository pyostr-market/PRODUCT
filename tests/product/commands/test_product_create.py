import json

import pytest

from src.catalog.product.api.schemas.schemas import ProductReadSchema

JPEG_BYTES = b"\xff\xd8\xff\xe0product-image"


@pytest.mark.asyncio
async def test_create_product_200(authorized_client):
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
            "image_is_main": "true",
        },
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert isinstance(product.id, int)
    assert product.name == "iPhone 15 Pro 256 Гб Красный"
    assert len(product.images) == 1
    assert product.images[0].is_main is True
    assert len(product.attributes) == 2


@pytest.mark.asyncio
async def test_create_product_400_name_too_short(authorized_client):
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
async def test_create_product_400_invalid_image(authorized_client):
    response = await authorized_client.post(
        "/product",
        data={
            "name": "Некорректный товар",
            "price": "10.00",
        },
        files=[("images", ("bad.jpg", b"1", "image/jpeg"))],
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_invalid_image"
