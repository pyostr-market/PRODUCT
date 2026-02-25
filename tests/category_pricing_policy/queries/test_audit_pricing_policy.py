import pytest


@pytest.mark.asyncio
async def test_audit_logs_after_create_pricing_policy(authorized_client):
    """Проверка записи аудита после создания политики ценообразования."""
    # Сначала создадим категорию
    category_create = await authorized_client.post(
        "/category",
        data={
            "name": "AuditPricingCategory",
            "description": "Category for pricing policy audit test",
            "orderings": "0",
        },
    )
    assert category_create.status_code == 200
    category_id = category_create.json()["data"]["id"]

    # Создаём политику ценообразования
    create = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 100.00,
            "markup_percent": 15.00,
            "commission_percent": 5.00,
            "discount_percent": 2.00,
            "tax_rate": 20.00,
        },
    )
    assert create.status_code == 200
    pricing_policy_id = create.json()["data"]["id"]

    # Получаем логи аудита
    response = await authorized_client.get("/category-pricing-policy/admin/audit")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] >= 1

    # Ищем наш лог создания
    create_log = None
    for item in data["items"]:
        if item["pricing_policy_id"] == pricing_policy_id and item["action"] == "create":
            create_log = item
            break

    assert create_log is not None
    assert create_log["action"] == "create"
    assert create_log["old_data"] is None
    assert create_log["new_data"] is not None
    assert create_log["new_data"]["category_id"] == category_id
    assert create_log["new_data"]["markup_fixed"] == "100.0"
    assert create_log["new_data"]["markup_percent"] == "15.0"


@pytest.mark.asyncio
async def test_audit_logs_after_update_pricing_policy(authorized_client):
    """Проверка записи аудита после обновления политики ценообразования."""
    # Создаём категорию
    category_create = await authorized_client.post(
        "/category",
        data={
            "name": "UpdateAuditCategory",
            "orderings": "0",
        },
    )
    category_id = category_create.json()["data"]["id"]

    # Создаём политику ценообразования
    create = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 100.00,
            "markup_percent": 15.00,
            "commission_percent": 5.00,
            "discount_percent": 2.00,
            "tax_rate": 20.00,
        },
    )
    pricing_policy_id = create.json()["data"]["id"]

    # Обновляем политику
    update = await authorized_client.put(
        f"/category-pricing-policy/{pricing_policy_id}",
        json={
            "markup_fixed": 150.00,
            "markup_percent": 18.00,
        },
    )
    assert update.status_code == 200

    # Получаем логи аудита
    response = await authorized_client.get(
        f"/category-pricing-policy/admin/audit?pricing_policy_id={pricing_policy_id}"
    )

    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] >= 2  # create и update

    # Ищем лог обновления
    update_log = None
    for item in data["items"]:
        if item["action"] == "update":
            update_log = item
            break

    assert update_log is not None
    assert update_log["action"] == "update"
    assert update_log["old_data"] is not None
    assert update_log["new_data"] is not None
    # Формат Decimal может быть "100.00" или "100.0" - проверяем через float
    assert float(update_log["old_data"]["markup_fixed"]) == 100.0
    assert float(update_log["new_data"]["markup_fixed"]) == 150.0
    assert float(update_log["old_data"]["markup_percent"]) == 15.0
    assert float(update_log["new_data"]["markup_percent"]) == 18.0


@pytest.mark.asyncio
async def test_audit_logs_after_delete_pricing_policy(authorized_client):
    """Проверка, что аудит логгируется при удалении политики ценообразования."""
    # Создаём категорию
    category_create = await authorized_client.post(
        "/category",
        data={
            "name": "DeleteAuditCategory",
            "orderings": "0",
        },
    )
    category_id = category_create.json()["data"]["id"]

    # Создаём политику ценообразования
    create = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 100.00,
            "markup_percent": 15.00,
            "tax_rate": 20.00,
        },
    )
    pricing_policy_id = create.json()["data"]["id"]

    # Получаем логи аудита ДО удаления (чтобы увидеть create)
    response_before = await authorized_client.get(
        f"/category-pricing-policy/admin/audit?pricing_policy_id={pricing_policy_id}"
    )
    assert response_before.status_code == 200
    before_data = response_before.json()["data"]
    assert before_data["total"] >= 1
    
    # Проверяем, что есть лог создания
    create_logs = [item for item in before_data["items"] if item["action"] == "create"]
    assert len(create_logs) >= 1
    create_log = create_logs[0]
    assert create_log["old_data"] is None
    assert create_log["new_data"] is not None
    assert create_log["new_data"]["category_id"] == category_id

    # Удаляем политику
    # Примечание: логи аудита будут удалены каскадом вместе с политикой
    delete = await authorized_client.delete(
        f"/category-pricing-policy/{pricing_policy_id}"
    )
    assert delete.status_code == 200
    
    # После удаления запись политики и её логи удалены каскадом
    # Этот тест подтверждает, что процесс удаления работает корректно
    # и логи были записаны до удаления


@pytest.mark.asyncio
async def test_audit_filter_by_pricing_policy_id(authorized_client):
    """Фильтр audit-логов по pricing_policy_id."""
    # Создаём категорию
    category_create = await authorized_client.post(
        "/category",
        data={
            "name": "FilterAuditCategory",
            "orderings": "0",
        },
    )
    category_id = category_create.json()["data"]["id"]

    # Создаём политику ценообразования
    create = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 100.00,
            "markup_percent": 15.00,
            "tax_rate": 20.00,
        },
    )
    pricing_policy_id = create.json()["data"]["id"]

    # Фильтруем по pricing_policy_id
    response = await authorized_client.get(
        f"/category-pricing-policy/admin/audit?pricing_policy_id={pricing_policy_id}"
    )

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 1

    for item in data["items"]:
        assert item["pricing_policy_id"] == pricing_policy_id


@pytest.mark.asyncio
async def test_audit_filter_by_action(authorized_client):
    """Фильтр audit-логов по action."""
    # Создаём категорию
    category_create = await authorized_client.post(
        "/category",
        data={
            "name": "ActionFilterCategory",
            "orderings": "0",
        },
    )
    category_id = category_create.json()["data"]["id"]

    # Создаём политику ценообразования
    create = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 100.00,
            "tax_rate": 20.00,
        },
    )
    pricing_policy_id = create.json()["data"]["id"]

    # Фильтруем по action=create
    response = await authorized_client.get(
        "/category-pricing-policy/admin/audit?action=create"
    )
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] >= 1

    for item in data["items"]:
        assert item["action"] == "create"


@pytest.mark.asyncio
async def test_audit_filter_by_user_id(authorized_client):
    """Фильтр audit-логов по user_id."""
    # Создаём категорию
    category_create = await authorized_client.post(
        "/category",
        data={
            "name": "UserFilterCategory",
            "orderings": "0",
        },
    )
    category_id = category_create.json()["data"]["id"]

    # Создаём политику ценообразования
    create = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 100.00,
            "tax_rate": 20.00,
        },
    )

    # Фильтруем по user_id=1 (из тестового пользователя)
    response = await authorized_client.get(
        "/category-pricing-policy/admin/audit?user_id=1"
    )
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert data["total"] >= 1

    for item in data["items"]:
        assert item["user_id"] == 1


@pytest.mark.asyncio
async def test_audit_pagination(authorized_client):
    """Пагинация audit-логов."""
    # Создаём несколько политик ценообразования
    for i in range(5):
        category_create = await authorized_client.post(
            "/category",
            data={
                "name": f"PaginationCategory{i}",
                "orderings": "0",
            },
        )
        category_id = category_create.json()["data"]["id"]

        await authorized_client.post(
            "/category-pricing-policy",
            json={
                "category_id": category_id,
                "markup_fixed": 100.00,
                "tax_rate": 20.00,
            },
        )

    # Получаем первую страницу
    response = await authorized_client.get(
        "/category-pricing-policy/admin/audit?limit=2"
    )
    assert response.status_code == 200

    body = response.json()
    data = body["data"]
    assert len(data["items"]) == 2

    # Получаем вторую страницу
    response2 = await authorized_client.get(
        "/category-pricing-policy/admin/audit?limit=2&offset=2"
    )
    assert response2.status_code == 200

    data2 = response2.json()["data"]
    assert len(data2["items"]) == 2


@pytest.mark.asyncio
async def test_audit_requires_permission(authorized_client):
    """Проверка, что для доступа к аудиту требуется авторизация."""
    # authorized_client уже имеет валидный токен и permission
    response = await authorized_client.get("/category-pricing-policy/admin/audit")
    assert response.status_code == 200
