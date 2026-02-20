import pytest

from src.catalog.category.api.schemas.schemas import CategoryReadSchema


@pytest.mark.asyncio
async def test_create_category_200(authorized_client):
    response = await authorized_client.post(
        "/category/",
        json={
            "name": "Электроника",
            "description": "Категория электроники",
            "images": [
                {
                    "image": "image-bytes",
                    "image_name": "test.jpg",
                    "ordering": 0,
                }
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    category = CategoryReadSchema(**body["data"])
    assert category.name == "Электроника"
    assert category.description == "Категория электроники"
    assert category.images[0].image_url == "https://test-s3.local/categories/test-image-uuid.img"
    assert isinstance(category.id, int)


@pytest.mark.asyncio
async def test_create_category_400_name_too_short(authorized_client):
    response = await authorized_client.post(
        "/category/",
        json={
            "name": "A",
            "images": [
                {
                    "image": "image-bytes",
                    "image_name": "test.jpg",
                    "ordering": 0,
                }
            ],
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_name_too_short"
