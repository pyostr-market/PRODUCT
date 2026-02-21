import pytest

from src.catalog.category.api.schemas.schemas import CategoryReadSchema

OLD_IMAGE_PATH =  "static/img/test.jpg"
NEW_IMAGE_PATH =  "static/img/test_2.jpg"

@pytest.mark.asyncio
async def test_update_category_200_full_update(authorized_client):
    with open(OLD_IMAGE_PATH, "rb") as f:
        old_image = f.read()

    create = await authorized_client.post(
        "/category",
        data={
            "name": "Старая категория",
            "description": "Старое описание",
            "orderings": "0",
        },
        files=[("images", ("old.jpg", old_image, "image/jpeg"))],
    )

    assert create.status_code == 200
    category_id = create.json()["data"]["id"]

    with open(NEW_IMAGE_PATH, "rb") as f:
        new_image = f.read()

    response = await authorized_client.put(
        f"/category/{category_id}",
        data={
            "name": "Новая категория",
            "description": "Новое описание",
            "orderings": "0",
        },
        files=[("images", ("new.jpg", new_image, "image/jpeg"))],
    )

    assert response.status_code == 200

    body = response.json()
    updated = CategoryReadSchema(**body["data"])

    assert updated.id == category_id
    assert updated.name == "Новая категория"
    assert updated.description == "Новое описание"

@pytest.mark.asyncio
async def test_update_category_404_not_found(authorized_client):
    response = await authorized_client.put(
        "/category/999999",
        data={
            "name": "Not found",
            "description": "Nope",
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_not_found"
