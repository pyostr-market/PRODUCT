import json

import pytest

from src.catalog.category.api.schemas.schemas import CategoryReadSchema


@pytest.mark.asyncio
async def test_get_category_200(authorized_client, client):
    # Загружаем два изображения
    with open("static/img/test.jpg", "rb") as f:
        image1_data = f.read()

    with open("static/img/test_2.jpg", "rb") as f:
        image2_data = f.read()

    upload1_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("get1.jpg", image1_data, "image/jpeg")},
    )
    assert upload1_response.status_code == 200
    upload_id_1 = upload1_response.json()["data"]["upload_id"]

    upload2_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("get2.jpg", image2_data, "image/jpeg")},
    )
    assert upload2_response.status_code == 200
    upload_id_2 = upload2_response.json()["data"]["upload_id"]

    create = await authorized_client.post(
        "/category",
        data={
            "name": "Категория для get",
            "description": "Описание",
            "images_json": json.dumps([
                {"upload_id": upload_id_2, "ordering": 2},
                {"upload_id": upload_id_1, "ordering": 1},
            ]),
        },
    )
    assert create.status_code == 200

    # Проверяем, что изображения созданы с правильным ordering
    create_images = create.json()["data"]["images"]
    assert len(create_images) == 2

    category_id = create.json()["data"]["id"]

    response = await client.get(f"/category/{category_id}")
    assert response.status_code == 200

    body = response.json()
    category = CategoryReadSchema(**body["data"])

    assert category.id == category_id
    assert category.name == "Категория для get"
    # Изображения сортируются по ordering (возрастание), поэтому сначала идёт ordering=1, потом ordering=2
    assert [image.ordering for image in category.images] == [1, 2]
    # Первое изображение в ответе (с ordering=1)
    assert category.images[0].upload_id == upload_id_1
    # Второе изображение в ответе (с ordering=2)
    assert category.images[1].upload_id == upload_id_2

    # Проверяем, что связанные данные возвращаются (даже если null)
    assert "parent" in body["data"]
    assert "manufacturer" in body["data"]


@pytest.mark.asyncio
async def test_get_category_200_with_parent(authorized_client, client):
    """Проверка получения категории с родительской категорией."""
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

    # Создаём родительскую категорию
    parent_resp = await authorized_client.post(
        "/category",
        data={
            "name": "Parent Category",
            "images_json": json.dumps([{"upload_id": upload_id, "ordering": 0}]),
        },
    )
    assert parent_resp.status_code == 200, f"Parent category create failed: {parent_resp.json()}"
    parent_id = parent_resp.json()["data"]["id"]

    # Загружаем ещё одно изображение для дочерней категории
    upload2_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("test2.jpg", image_data, "image/jpeg")},
    )
    assert upload2_response.status_code == 200
    upload_id_2 = upload2_response.json()["data"]["upload_id"]

    # Создаём дочернюю категорию
    child_resp = await authorized_client.post(
        "/category",
        data={
            "name": "Child Category",
            "parent_id": str(parent_id),
            "images_json": json.dumps([{"upload_id": upload_id_2, "ordering": 0}]),
        },
    )
    assert child_resp.status_code == 200, f"Child category create failed: {child_resp.json()}"
    child_id = child_resp.json()["data"]["id"]

    response = await client.get(f"/category/{child_id}")
    assert response.status_code == 200

    body = response.json()

    # Проверяем, что родительская категория вернулась как вложенный объект
    assert body["data"]["parent"] is not None
    assert body["data"]["parent"]["id"] == parent_id
    assert body["data"]["parent"]["name"] == "Parent Category"


@pytest.mark.asyncio
async def test_get_category_200_with_manufacturer(authorized_client, client):
    """Проверка получения категории с производителем."""
    # Создаём производителя
    manuf_resp = await authorized_client.post(
        "/manufacturer",
        json={"name": "Test Manufacturer", "description": "Test Desc"},
    )
    assert manuf_resp.status_code == 200, f"Manufacturer create failed: {manuf_resp.json()}"
    manufacturer_id = manuf_resp.json()["data"]["id"]

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

    # Создаём категорию с производителем
    cat_resp = await authorized_client.post(
        "/category",
        data={
            "name": "Category with Manufacturer",
            "manufacturer_id": str(manufacturer_id),
            "images_json": json.dumps([{"upload_id": upload_id, "ordering": 0}]),
        },
    )
    assert cat_resp.status_code == 200, f"Category create failed: {cat_resp.json()}"
    category_id = cat_resp.json()["data"]["id"]

    response = await client.get(f"/category/{category_id}")
    assert response.status_code == 200

    body = response.json()

    # Проверяем, что производитель вернулся как вложенный объект
    assert body["data"]["manufacturer"] is not None
    assert body["data"]["manufacturer"]["id"] == manufacturer_id
    assert body["data"]["manufacturer"]["name"] == "Test Manufacturer"
    assert body["data"]["manufacturer"]["description"] == "Test Desc"


@pytest.mark.asyncio
async def test_get_category_404_not_found(client):
    response = await client.get("/category/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_not_found"
