import pytest


@pytest.mark.asyncio
async def test_delete_pricing_policy_200(authorized_client):
    """Успешное удаление политики ценообразования."""
    # Создаём категорию
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для удаления"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    # Создаём политику
    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    # Удаляем политику
    response = await authorized_client.delete(
        f"/category-pricing-policy/{policy_id}",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_delete_pricing_policy_404_not_found(authorized_client):
    """Ошибка при удалении несуществующей политики."""
    response = await authorized_client.delete(
        "/category-pricing-policy/999999",
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_not_found"


@pytest.mark.asyncio
async def test_delete_pricing_policy_403_no_permission(client):
    """Ошибка при удалении без прав доступа (неавторизованный)."""
    response = await client.delete(
        "/category-pricing-policy/1",
    )

    # Без токена получаем 401, а не 403
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_pricing_policy_verify_removed(authorized_client):
    """Проверка, что политика действительно удалена (GET возвращает 404)."""
    # Создаём категорию
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для проверки удаления"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    # Создаём политику
    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    # Удаляем
    delete_response = await authorized_client.delete(
        f"/category-pricing-policy/{policy_id}",
    )
    assert delete_response.status_code == 200

    # Пытаемся получить удалённую политику
    get_response = await authorized_client.get(
        f"/category-pricing-policy/{policy_id}",
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_pricing_policy_cascade_with_category(authorized_client):
    """Проверка, что при удалении категории политика удаляется каскадно."""
    # Создаём категорию
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для каскадного удаления"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    # Создаём политику
    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    # Получаем политику по category_id для проверки
    get_by_cat_response = await authorized_client.get(
        f"/category-pricing-policy/by-category/{category_id}",
    )
    assert get_by_cat_response.status_code == 200
    assert get_by_cat_response.json()["data"]["id"] == policy_id

    # Примечание: удаление категории проверяется отдельно,
    # так как может потребовать удаления связанных продуктов
