import json

import pytest

from src.catalog.category.api.schemas.schemas import CategoryReadSchema


@pytest.mark.asyncio
async def test_update_category_200_full_update(authorized_client):
    # Загружаем старое изображение
    with open("static/img/test.jpg", "rb") as f:
        old_image_data = f.read()

    old_upload_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("old.jpg", old_image_data, "image/jpeg")},
    )
    assert old_upload_response.status_code == 200
    old_upload_id = old_upload_response.json()["data"]["upload_id"]

    # Создаём категорию
    create_response = await authorized_client.post(
        "/category",
        data={
            "name": "Старая категория",
            "description": "Старое описание",
            "images_json": json.dumps([{"upload_id": old_upload_id, "ordering": 0}]),
        },
    )
    assert create_response.status_code == 200
    category_id = create_response.json()["data"]["id"]

    # Загружаем новое изображение
    with open("static/img/test_2.jpg", "rb") as f:
        new_image_data = f.read()

    new_upload_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("new.jpg", new_image_data, "image/jpeg")},
    )
    assert new_upload_response.status_code == 200
    new_upload_id = new_upload_response.json()["data"]["upload_id"]

    # Обновляем категорию с операциями над изображениями
    response = await authorized_client.put(
        f"/category/{category_id}",
        data={
            "name": "Новая категория",
            "description": "Новое описание",
            "images_json": json.dumps([
                {"action": "delete", "upload_id": old_upload_id},
                {"action": "create", "upload_id": new_upload_id, "ordering": 0},
            ]),
        },
    )

    assert response.status_code == 200

    body = response.json()
    updated = CategoryReadSchema(**body["data"])

    assert updated.id == category_id
    assert updated.name == "Новая категория"
    assert updated.description == "Новое описание"
    assert len(updated.images) == 1
    assert updated.images[0].upload_id == new_upload_id


@pytest.mark.asyncio
async def test_update_category_200_pass_image(authorized_client):
    # Загружаем изображение
    with open("static/img/test.jpg", "rb") as f:
        image_data = f.read()

    upload_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("test.jpg", image_data, "image/jpeg")},
    )
    assert upload_response.status_code == 200
    upload_id = upload_response.json()["data"]["upload_id"]

    # Создаём категорию
    create_response = await authorized_client.post(
        "/category",
        data={
            "name": "Категория",
            "description": "Описание",
            "images_json": json.dumps([{"upload_id": upload_id, "ordering": 0}]),
        },
    )
    assert create_response.status_code == 200
    category_id = create_response.json()["data"]["id"]

    # Обновляем категорию, сохраняя изображение (pass)
    response = await authorized_client.put(
        f"/category/{category_id}",
        data={
            "name": "Обновлённая категория",
            "images_json": json.dumps([
                {"action": "pass", "upload_id": upload_id, "ordering": 0},
            ]),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["name"] == "Обновлённая категория"
    assert len(body["data"]["images"]) == 1
    assert body["data"]["images"][0]["upload_id"] == upload_id


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


@pytest.mark.asyncio
async def test_update_category_400_invalid_images_json(authorized_client):
    response = await authorized_client.put(
        "/category/999999",
        data={
            "name": "Test",
            "images_json": "not-a-json",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_invalid_image"
