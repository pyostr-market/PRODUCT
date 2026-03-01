import pytest

from src.catalog.category.api.schemas.schemas import CategoryPricingPolicyReadSchema


@pytest.mark.asyncio
async def test_get_pricing_policy_by_category_200(authorized_client):
    """Успешное получение политики по ID категории."""
    # Создаём категорию
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для получения по ID"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    # Создаём политику
    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 200.00,
            "markup_percent": 20.00,
            "tax_rate": 25.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    # Получаем политику по category_id
    response = await authorized_client.get(
        f"/category-pricing-policy/by-category/{category_id}",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    policy = CategoryPricingPolicyReadSchema(**body["data"])
    assert policy.id == policy_id
    assert policy.category_id == category_id
    assert policy.markup_fixed == 200.00
    assert policy.markup_percent == 20.00
    assert policy.tax_rate == 25.00


@pytest.mark.asyncio
async def test_get_pricing_policy_by_category_404_not_found(authorized_client):
    """Ошибка при получении политики для категории без политики."""
    # Создаём категорию без политики
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория без политики"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    # Пытаемся получить политику
    response = await authorized_client.get(
        f"/category-pricing-policy/by-category/{category_id}",
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_not_found"


@pytest.mark.asyncio
async def test_get_pricing_policy_by_category_404_category_not_found(authorized_client):
    """Ошибка при получении политики для несуществующей категории."""
    response = await authorized_client.get(
        "/category-pricing-policy/by-category/999999",
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_not_found"


@pytest.mark.asyncio
async def test_get_pricing_policy_by_category_403_no_permission(client):
    """Ошибка при получении без прав доступа (неавторизованный)."""
    response = await client.get(
        "/category-pricing-policy/by-category/1",
    )

    # Без токена получаем 401, а не 403
    assert response.status_code == 401
