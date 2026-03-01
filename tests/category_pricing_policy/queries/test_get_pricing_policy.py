import pytest

from src.catalog.category.api.schemas.schemas import CategoryPricingPolicyReadSchema


@pytest.mark.asyncio
async def test_get_pricing_policy_200(authorized_client):
    """Успешное получение политики ценообразования по ID."""
    # Создаём категорию
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для получения"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    # Создаём политику
    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 150.00,
            "markup_percent": 15.00,
            "commission_percent": 5.00,
            "discount_percent": 3.00,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    # Получаем политику
    response = await authorized_client.get(
        f"/category-pricing-policy/{policy_id}",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    policy = CategoryPricingPolicyReadSchema(**body["data"])
    assert policy.id == policy_id
    assert policy.category_id == category_id
    assert policy.markup_fixed == 150.00
    assert policy.markup_percent == 15.00
    assert policy.commission_percent == 5.00
    assert policy.discount_percent == 3.00
    assert policy.tax_rate == 20.00


@pytest.mark.asyncio
async def test_get_pricing_policy_404_not_found(authorized_client):
    """Ошибка при получении несуществующей политики."""
    response = await authorized_client.get(
        "/category-pricing-policy/999999",
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_not_found"


@pytest.mark.asyncio
async def test_get_pricing_policy_403_no_permission(client):
    """Ошибка при получении без прав доступа (неавторизованный)."""
    response = await client.get(
        "/category-pricing-policy/1",
    )

    # Без токена получаем 401, а не 403
    assert response.status_code == 401
