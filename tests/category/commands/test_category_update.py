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
        json={
            "name": "Старая категория",
            "description": "Старое описание",
            "image": {"upload_id": old_upload_id},
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

    # Обновляем категорию с операцией над изображением
    response = await authorized_client.put(
        f"/category/{category_id}",
        json={
            "name": "Новая категория",
            "description": "Новое описание",
            "image": {
                "action": "update",
                "upload_id": new_upload_id,
            },
        },
    )

    assert response.status_code == 200

    body = response.json()
    updated = CategoryReadSchema(**body["data"])

    assert updated.id == category_id
    assert updated.name == "Новая категория"
    assert updated.description == "Новое описание"
    assert updated.image is not None
    assert updated.image.upload_id == new_upload_id


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
        json={
            "name": "Категория",
            "description": "Описание",
            "image": {"upload_id": upload_id},
        },
    )
    assert create_response.status_code == 200
    category_id = create_response.json()["data"]["id"]

    # Обновляем категорию, сохраняя изображение (pass)
    response = await authorized_client.put(
        f"/category/{category_id}",
        json={
            "name": "Обновлённая категория",
            "image": {
                "action": "pass",
                "upload_id": upload_id,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["name"] == "Обновлённая категория"
    assert body["data"]["image"] is not None
    assert body["data"]["image"]["upload_id"] == upload_id


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


@pytest.mark.asyncio
async def test_update_category_400_invalid_image(authorized_client):
    response = await authorized_client.put(
        "/category/999999",
        json={
            "name": "Test",
            "image": "not-an-object",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_category_circular_dependency_self_reference(authorized_client):
    """Тест: категория не может стать родителем самой себя."""
    # Создаём категорию
    create_response = await authorized_client.post(
        "/category",
        json={
            "name": "Тестовая категория",
            "description": "Описание",
        },
    )
    assert create_response.status_code == 200
    category_id = create_response.json()["data"]["id"]

    # Пытаемся установить parent_id равным самому себе
    response = await authorized_client.put(
        f"/category/{category_id}",
        json={
            "name": "Тестовая категория",
            "parent_id": category_id,
        },
    )

    # Ожидаем ошибку (400 или 500 в зависимости от реализации)
    assert response.status_code in [400, 500]
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_update_category_circular_dependency_child_parent(authorized_client):
    """Тест: родитель не может стать дочерним элементом своего потомка."""
    # Создаём родительскую категорию
    parent_response = await authorized_client.post(
        "/category",
        json={
            "name": "Родитель",
            "description": "Родительская категория",
        },
    )
    assert parent_response.status_code == 200
    parent_id = parent_response.json()["data"]["id"]

    # Создаём дочернюю категорию
    child_response = await authorized_client.post(
        "/category",
        json={
            "name": "Дочка",
            "description": "Дочерняя категория",
            "parent_id": parent_id,
        },
    )
    assert child_response.status_code == 200
    child_id = child_response.json()["data"]["id"]

    # Пытаемся сделать родителя дочерним элементом потомка (цикл!)
    response = await authorized_client.put(
        f"/category/{parent_id}",
        json={
            "name": "Родитель",
            "parent_id": child_id,  # Пытаемся сделать родителя дочерним элементом
        },
    )

    # Ожидаем ошибку циклической зависимости
    assert response.status_code in [400, 500]
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_update_category_change_parent_id_valid(authorized_client):
    """Тест: успешное изменение parent_id на валидное значение (без цикла)."""
    # Создаём две независимые категории
    parent1_response = await authorized_client.post(
        "/category",
        json={
            "name": "Родитель 1",
            "description": "Первая родительская категория",
        },
    )
    assert parent1_response.status_code == 200
    parent1_id = parent1_response.json()["data"]["id"]

    parent2_response = await authorized_client.post(
        "/category",
        json={
            "name": "Родитель 2",
            "description": "Вторая родительская категория",
        },
    )
    assert parent2_response.status_code == 200
    parent2_id = parent2_response.json()["data"]["id"]

    # Создаём дочернюю категорию с parent1
    child_response = await authorized_client.post(
        "/category",
        json={
            "name": "Дочка",
            "description": "Дочерняя категория",
            "parent_id": parent1_id,
        },
    )
    assert child_response.status_code == 200
    child_id = child_response.json()["data"]["id"]

    # Обновляем дочернюю категорию, меняя родителя с parent1 на parent2
    response = await authorized_client.put(
        f"/category/{child_id}",
        json={
            "name": "Дочка",
            "parent_id": parent2_id,  # Меняем родителя на другой
        },
    )

    # Ожидаем успех
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == child_id
    assert body["data"]["parent"]["id"] == parent2_id
