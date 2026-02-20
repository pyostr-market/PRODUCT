import pytest

from src.catalog.category.api.schemas.schemas import CategoryReadSchema


@pytest.mark.asyncio
async def test_update_category_200_full_update(authorized_client):
    create = await authorized_client.post(
        "/category/",
        json={
            "name": "Старая категория",
            "description": "Старое описание",
            "images": [
                {
                    "image": "old-image",
                    "image_name": "old.jpg",
                    "ordering": 0,
                }
            ],
        },
    )

    assert create.status_code == 200
    category_id = create.json()["data"]["id"]

    response = await authorized_client.put(
        f"/category/{category_id}",
        json={
            "name": "Новая категория",
            "description": "Новое описание",
            "images": [
                {
                    "image": "new-image",
                    "image_name": "new.jpg",
                    "ordering": 0,
                }
            ],
        },
    )

    assert response.status_code == 200

    body = response.json()
    updated = CategoryReadSchema(**body["data"])

    assert updated.id == category_id
    assert updated.name == "Новая категория"
    assert updated.description == "Новое описание"
    assert updated.images[0].image_url == "https://test-s3.local/categories/test-image-uuid.img"


@pytest.mark.asyncio
async def test_update_category_404_not_found(authorized_client):
    response = await authorized_client.put(
        "/category/999999",
        json={
            "name": "Not found",
            "description": "Nope",
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_not_found"
