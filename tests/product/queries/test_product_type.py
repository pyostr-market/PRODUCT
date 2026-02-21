import pytest

from src.catalog.product.api.schemas.product_type import ProductTypeReadSchema


@pytest.mark.asyncio
async def test_get_product_type_200(authorized_client, client):
    """Получить тип продукта по ID"""
    # Создаём тип
    create = await authorized_client.post(
        "/product/type",
        json={"name": "Test Type", "parent_id": None}
    )
    assert create.status_code == 200
    type_id = create.json()["data"]["id"]

    # Получаем
    response = await client.get(f"/product/type/{type_id}")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body

    product_type = ProductTypeReadSchema(**body["data"])
    assert product_type.name == "Test Type"


@pytest.mark.asyncio
async def test_get_product_type_404(client):
    """Тип не найден"""
    response = await client.get("/product/type/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_filter_product_type_list_200(authorized_client, client):
    """Получить список типов продуктов"""
    # Создаём типы
    for name in ["Type A", "Type B", "Type C"]:
        await authorized_client.post(
            "/product/type",
            json={"name": name, "parent_id": None}
        )

    response = await client.get("/product/type")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_filter_product_type_by_name(authorized_client, client):
    """Фильтрация типов по имени"""
    await authorized_client.post(
        "/product/type", json={"name": "FilterPhones", "parent_id": None}
    )
    await authorized_client.post(
        "/product/type", json={"name": "FilterLaptops", "parent_id": None}
    )
    await authorized_client.post(
        "/product/type", json={"name": "Other", "parent_id": None}
    )

    response = await client.get("/product/type?name=Filter")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_filter_product_type_limit(authorized_client, client):
    """Лимит для типов продуктов"""
    for i in range(5):
        await authorized_client.post(
            "/product/type", json={"name": f"Type {i}", "parent_id": None}
        )

    response = await client.get("/product/type?limit=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_filter_product_type_offset(authorized_client, client):
    """Offset для типов продуктов"""
    for i in range(5):
        await authorized_client.post(
            "/product/type", json={"name": f"Type {i}", "parent_id": None}
        )

    response = await client.get("/product/type?limit=2&offset=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_create_product_type_200(authorized_client):
    """Создать тип продукта"""
    response = await authorized_client.post(
        "/product/type",
        json={"name": "New Type", "parent_id": None}
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body

    product_type = ProductTypeReadSchema(**body["data"])
    assert product_type.name == "New Type"


@pytest.mark.asyncio
async def test_create_product_type_with_parent(authorized_client):
    """Создать тип продукта с родителем"""
    # Создаём родителя
    parent = await authorized_client.post(
        "/product/type", json={"name": "Parent Type", "parent_id": None}
    )
    parent_id = parent.json()["data"]["id"]

    # Создаём ребёнка
    response = await authorized_client.post(
        "/product/type",
        json={"name": "Child Type", "parent_id": parent_id}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["parent_id"] == parent_id


@pytest.mark.asyncio
async def test_update_product_type_200(authorized_client):
    """Обновить тип продукта"""
    # Создаём
    create = await authorized_client.post(
        "/product/type", json={"name": "Old Name", "parent_id": None}
    )
    type_id = create.json()["data"]["id"]

    # Обновляем
    response = await authorized_client.put(
        f"/product/type/{type_id}",
        json={"name": "New Name", "parent_id": None}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["name"] == "New Name"


@pytest.mark.asyncio
async def test_update_product_type_404(authorized_client):
    """Обновление несуществующего типа"""
    response = await authorized_client.put(
        "/product/type/99999",
        json={"name": "New Name", "parent_id": None}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_type_200(authorized_client):
    """Удалить тип продукта"""
    # Создаём
    create = await authorized_client.post(
        "/product/type", json={"name": "To Delete", "parent_id": None}
    )
    type_id = create.json()["data"]["id"]

    # Удаляем
    response = await authorized_client.delete(f"/product/type/{type_id}")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True

    # Проверяем, что удалён
    get_response = await authorized_client.get(f"/product/type/{type_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_type_404(authorized_client):
    """Удаление несуществующего типа"""
    response = await authorized_client.delete("/product/type/99999")
    assert response.status_code == 404
