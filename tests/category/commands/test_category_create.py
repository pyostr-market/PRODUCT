from pathlib import Path

import pytest

from src.catalog.category.api.schemas.schemas import CategoryReadSchema

TEST_IMAGE_PATH = "static/img/test.jpg"

@pytest.mark.asyncio
async def test_create_category_200(authorized_client):
    with open(TEST_IMAGE_PATH, "rb") as f:
        image_bytes = f.read()

    response = await authorized_client.post(
        "/category",
        data={
            "name": "Электроника",
            "description": "Категория электроники",
            "orderings": "0",
        },
        files=[("images", ("test.jpg", image_bytes, "image/jpeg"))],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    category = CategoryReadSchema(**body["data"])
    assert category.name == "Электроника"
    assert category.description == "Категория электроники"
    assert isinstance(category.id, int)


@pytest.mark.asyncio
async def test_create_category_400_name_too_short(authorized_client):
    with open(TEST_IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
    response = await authorized_client.post(
        "/category",
        data={
            "name": "A",
            "orderings": "0",
        },
        files=[("images", ("test.jpg", image_bytes, "image/jpeg"))],
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_name_too_short"


@pytest.mark.asyncio
async def test_create_category_400_invalid_image(authorized_client):
    response = await authorized_client.post(
        "/category",
        data={"name": "Категория", "orderings": "0"},
        files=[("images", ("test.jpg", b"1", "image/jpeg"))],
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_invalid_image"
