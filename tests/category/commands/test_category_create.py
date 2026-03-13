import json

import pytest

from src.catalog.category.api.schemas.schemas import CategoryReadSchema


@pytest.mark.asyncio
async def test_create_category_200(authorized_client):
    # Сначала загружаем изображение через upload эндпоинт
    with open("static/img/test.jpg", "rb") as f:
        image_data = f.read()

    upload_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("test.jpg", image_data, "image/jpeg")},
    )
    assert upload_response.status_code == 200
    upload_id = upload_response.json()["data"]["upload_id"]

    # Создаём категорию с image
    response = await authorized_client.post(
        "/category",
        json={
            "name": "Электроника",
            "description": "Категория электроники",
            "image": {"upload_id": upload_id},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    category = CategoryReadSchema(**body["data"])
    assert category.name == "Электроника"
    assert category.description == "Категория электроники"
    assert isinstance(category.id, int)
    assert category.image is not None
    assert category.image.upload_id == upload_id


@pytest.mark.asyncio
async def test_create_category_400_name_too_short(authorized_client):
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

    response = await authorized_client.post(
        "/category",
        json={
            "name": "A",
            "image": {"upload_id": upload_id},
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_name_too_short"


@pytest.mark.asyncio
async def test_create_category_400_invalid_image(authorized_client):
    # Передаём некорректные image
    response = await authorized_client.post(
        "/category",
        json={
            "name": "Категория",
            "image": "not-an-object",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_category_400_upload_not_found(authorized_client):
    # Передаём несуществующий upload_id
    response = await authorized_client.post(
        "/category",
        json={
            "name": "Категория",
            "image": {"upload_id": 99999},
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_invalid_image"
