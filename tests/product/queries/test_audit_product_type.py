import pytest


@pytest.mark.asyncio
async def test_product_type_audit_logs_200(authorized_client):
    """Проверка аудит-логов для типов продуктов"""
    # Создаём тип
    create = await authorized_client.post(
        "/product/type",
        json={"name": "Audit Type", "parent_id": None}
    )
    assert create.status_code == 200
    type_id = create.json()["data"]["id"]

    # Обновляем
    update = await authorized_client.put(
        f"/product/type/{type_id}",
        json={"name": "Audit Type Updated", "parent_id": None}
    )
    assert update.status_code == 200

    # Получаем аудит-логи
    response = await authorized_client.get(f"/product/admin/type/audit?product_type_id={type_id}")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["total"] >= 2
    assert len(data["items"]) >= 2

    actions = [item["action"] for item in data["items"]]
    assert "create" in actions
    assert "update" in actions


@pytest.mark.asyncio
async def test_product_type_audit_filter_by_type_id(authorized_client):
    """Фильтрация аудит-логов по ID типа продукта"""
    # Создаём два типа
    type1 = await authorized_client.post(
        "/product/type", json={"name": "Type 1", "parent_id": None}
    )
    type1_id = type1.json()["data"]["id"]

    type2 = await authorized_client.post(
        "/product/type", json={"name": "Type 2", "parent_id": None}
    )
    type2_id = type2.json()["data"]["id"]

    # Обновляем только первый
    await authorized_client.put(
        f"/product/type/{type1_id}",
        json={"name": "Type 1 Updated", "parent_id": None}
    )

    # Фильтруем по первому
    response = await authorized_client.get(f"/product/admin/type/audit?product_type_id={type1_id}")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    # Все записи должны относиться к type1
    for item in data["items"]:
        assert item.get("product_type_id") == type1_id


@pytest.mark.asyncio
async def test_product_type_audit_filter_by_action(authorized_client):
    """Фильтрация аудит-логов по действию"""
    # Создаём тип
    create = await authorized_client.post(
        "/product/type", json={"name": "Action Type", "parent_id": None}
    )
    type_id = create.json()["data"]["id"]

    # Фильтруем по create
    response = await authorized_client.get(f"/product/admin/type/audit?action=create")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    # Все записи должны быть create
    for item in data["items"]:
        assert item["action"] == "create"


@pytest.mark.asyncio
async def test_product_type_audit_pagination(authorized_client):
    """Пагинация аудит-логов"""
    # Создаём несколько типов
    for i in range(5):
        await authorized_client.post(
            "/product/type", json={"name": f"Paginated Type {i}", "parent_id": None}
        )

    # Получаем с лимитом
    response = await authorized_client.get("/product/admin/type/audit?limit=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert len(data["items"]) == 2

    # Получаем со сдвигом
    response2 = await authorized_client.get("/product/admin/type/audit?limit=2&offset=2")
    assert response2.status_code == 200

    data2 = response2.json()["data"]
    assert len(data2["items"]) == 2
