import pytest

from src.catalog.product.api.schemas.product_type import ProductTypeReadSchema


@pytest.mark.asyncio
async def test_get_product_type_tree_200(authorized_client, client):
    """Проверка получения дерева типов продуктов."""
    # Создаём корневой тип 1
    root1_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Root Type 1", "parent_id": None}
    )
    assert root1_resp.status_code == 200
    root1_id = root1_resp.json()["data"]["id"]

    # Создаём корневой тип 2
    root2_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Root Type 2", "parent_id": None}
    )
    assert root2_resp.status_code == 200
    root2_id = root2_resp.json()["data"]["id"]

    # Создаём дочерний тип для root1
    child1_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Child Type 1", "parent_id": root1_id}
    )
    assert child1_resp.status_code == 200
    child1_id = child1_resp.json()["data"]["id"]

    # Получаем дерево типов продуктов
    response = await client.get("/product/type/tree")
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

    # Проверяем корневой тип 1
    assert root1["name"] == "Root Type 1"
    assert root1["parent_id"] is None
    assert len(root1["children"]) == 1

    # Проверяем дочерний тип
    child1 = root1["children"][0]
    assert child1["id"] == child1_id
    assert child1["name"] == "Child Type 1"
    assert child1["parent_id"] == root1_id
    assert len(child1["children"]) == 0

    # Проверяем корневой тип 2 (без детей)
    assert root2["name"] == "Root Type 2"
    assert root2["parent_id"] is None
    assert len(root2["children"]) == 0


@pytest.mark.asyncio
async def test_get_product_type_tree_empty(client):
    """Проверка получения дерева типов при отсутствии типов."""
    response = await client.get("/product/type/tree")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 0
    assert body["data"]["items"] == []


@pytest.mark.asyncio
async def test_get_product_type_tree_schema(authorized_client, client):
    """Проверка, что ответ соответствует схеме ProductTypeReadSchema."""
    # Создаём тип
    type_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Schema Test Type", "parent_id": None}
    )
    assert type_resp.status_code == 200

    response = await client.get("/product/type/tree")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    # Валидируем схему
    type_item = body["data"]["items"][0]
    schema = ProductTypeReadSchema(**type_item)

    assert schema.id == type_resp.json()["data"]["id"]
    assert schema.name == "Schema Test Type"
    assert schema.parent_id is None
    assert schema.children == []


@pytest.mark.asyncio
async def test_get_product_type_tree_deep_hierarchy(authorized_client, client):
    """Проверка дерева с глубокой иерархией (3 уровня)."""
    # Уровень 1
    level1_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Level 1", "parent_id": None}
    )
    assert level1_resp.status_code == 200
    level1_id = level1_resp.json()["data"]["id"]

    # Уровень 2
    level2_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Level 2", "parent_id": level1_id}
    )
    assert level2_resp.status_code == 200
    level2_id = level2_resp.json()["data"]["id"]

    # Уровень 3
    level3_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Level 3", "parent_id": level2_id}
    )
    assert level3_resp.status_code == 200
    level3_id = level3_resp.json()["data"]["id"]

    # Получаем дерево
    response = await client.get("/product/type/tree")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 3

    items = body["data"]["items"]
    assert len(items) == 1

    # Проверяем иерархию
    level1 = items[0]
    assert level1["name"] == "Level 1"
    assert level1["parent_id"] is None
    assert len(level1["children"]) == 1

    level2 = level1["children"][0]
    assert level2["name"] == "Level 2"
    assert level2["parent_id"] == level1_id
    assert len(level2["children"]) == 1

    level3 = level2["children"][0]
    assert level3["name"] == "Level 3"
    assert level3["parent_id"] == level2_id
    assert len(level3["children"]) == 0


@pytest.mark.asyncio
async def test_get_product_type_tree_multiple_children(authorized_client, client):
    """Проверка дерева с несколькими дочерними элементами."""
    # Создаём корень
    root_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Root", "parent_id": None}
    )
    assert root_resp.status_code == 200
    root_id = root_resp.json()["data"]["id"]

    # Создаём 5 дочерних типов
    child_ids = []
    for i in range(5):
        child_resp = await authorized_client.post(
            "/product/type",
            json={"name": f"Child {i}", "parent_id": root_id}
        )
        assert child_resp.status_code == 200
        child_ids.append(child_resp.json()["data"]["id"])

    # Получаем дерево
    response = await client.get("/product/type/tree")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 6

    items = body["data"]["items"]
    root = next(item for item in items if item["id"] == root_id)

    # Проверяем, что все дети на месте
    assert len(root["children"]) == 5
    child_names = {child["name"] for child in root["children"]}
    assert child_names == {"Child 0", "Child 1", "Child 2", "Child 3", "Child 4"}
