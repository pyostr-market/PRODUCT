import json

import pytest

from src.catalog.category.api.schemas.schemas import CategoryTreeSchema


@pytest.mark.asyncio
async def test_get_category_tree_200(authorized_client, client):
    """Проверка получения дерева категорий."""
    # Загружаем изображения
    with open("static/img/test.jpg", "rb") as f:
        image_data = f.read()

    upload1_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("tree1.jpg", image_data, "image/jpeg")},
    )
    assert upload1_response.status_code == 200
    upload_id_1 = upload1_response.json()["data"]["upload_id"]

    upload2_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("tree2.jpg", image_data, "image/jpeg")},
    )
    assert upload2_response.status_code == 200
    upload_id_2 = upload2_response.json()["data"]["upload_id"]

    upload3_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("tree3.jpg", image_data, "image/jpeg")},
    )
    assert upload3_response.status_code == 200
    upload_id_3 = upload3_response.json()["data"]["upload_id"]

    # Создаём корневую категорию 1
    root1_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Root Category 1",
            "description": "First root category",
            "images": [{"upload_id": upload_id_1, "ordering": 0}],
        },
    )
    assert root1_resp.status_code == 200
    root1_id = root1_resp.json()["data"]["id"]

    # Создаём корневую категорию 2
    root2_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Root Category 2",
            "description": "Second root category",
            "images": [{"upload_id": upload_id_2, "ordering": 0}],
        },
    )
    assert root2_resp.status_code == 200
    root2_id = root2_resp.json()["data"]["id"]

    # Создаём дочернюю категорию для root1
    child1_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Child Category 1",
            "description": "Child of root 1",
            "parent_id": root1_id,
            "images": [{"upload_id": upload_id_3, "ordering": 0}],
        },
    )
    assert child1_resp.status_code == 200
    child1_id = child1_resp.json()["data"]["id"]

    # Получаем дерево категорий
    response = await client.get("/category/tree")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "items" in body["data"]
    assert body["data"]["total"] == 3

    items = body["data"]["items"]

    # Проверяем, что вернулись 2 корневые категории
    assert len(items) == 2

    # Находим корневые категории по ID
    root1 = next(item for item in items if item["id"] == root1_id)
    root2 = next(item for item in items if item["id"] == root2_id)

    # Проверяем корневую категорию 1
    assert root1["name"] == "Root Category 1"
    assert root1["description"] == "First root category"
    assert root1["parent_id"] is None
    assert len(root1["children"]) == 1

    # Проверяем дочернюю категорию
    child1 = root1["children"][0]
    assert child1["id"] == child1_id
    assert child1["name"] == "Child Category 1"
    assert child1["description"] == "Child of root 1"
    assert child1["parent_id"] == root1_id
    assert len(child1["children"]) == 0

    # Проверяем корневую категорию 2 (без детей)
    assert root2["name"] == "Root Category 2"
    assert root2["description"] == "Second root category"
    assert root2["parent_id"] is None
    assert len(root2["children"]) == 0


@pytest.mark.asyncio
async def test_get_category_tree_empty(client):
    """Проверка получения дерева категорий при отсутствии категорий."""
    response = await client.get("/category/tree")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 0
    assert body["data"]["items"] == []


@pytest.mark.asyncio
async def test_get_category_tree_schema(authorized_client, client):
    """Проверка, что ответ соответствует схеме CategoryTreeSchema."""
    with open("static/img/test.jpg", "rb") as f:
        image_data = f.read()

    upload_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("schema_test.jpg", image_data, "image/jpeg")},
    )
    assert upload_response.status_code == 200
    upload_id = upload_response.json()["data"]["upload_id"]

    # Создаём категорию
    cat_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Schema Test Category",
            "images": [{"upload_id": upload_id, "ordering": 0}],
        },
    )
    assert cat_resp.status_code == 200

    response = await client.get("/category/tree")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    # Валидируем схему
    tree_item = body["data"]["items"][0]
    schema = CategoryTreeSchema(**tree_item)

    assert schema.id == cat_resp.json()["data"]["id"]
    assert schema.name == "Schema Test Category"
    assert schema.parent_id is None
    assert schema.children == []
