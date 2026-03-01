import pytest

from src.catalog.category.api.schemas.schemas import CategoryPricingPolicyReadSchema


@pytest.mark.asyncio
async def test_update_pricing_policy_200_full_update(authorized_client):
    """Успешное полное обновление политики ценообразования."""
    # Создаём категорию
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для обновления"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    # Создаём политику
    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 100.00,
            "markup_percent": 10.00,
            "commission_percent": 5.00,
            "discount_percent": 2.00,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    # Обновляем политику
    response = await authorized_client.put(
        f"/category-pricing-policy/{policy_id}",
        json={
            "markup_fixed": 200.00,
            "markup_percent": 20.00,
            "commission_percent": 10.00,
            "discount_percent": 5.00,
            "tax_rate": 25.00,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    policy = CategoryPricingPolicyReadSchema(**body["data"])
    assert policy.id == policy_id
    assert policy.category_id == category_id
    assert policy.markup_fixed == 200.00
    assert policy.markup_percent == 20.00
    assert policy.commission_percent == 10.00
    assert policy.discount_percent == 5.00
    assert policy.tax_rate == 25.00


@pytest.mark.asyncio
async def test_update_pricing_policy_200_partial_update(authorized_client):
    """Успешное частичное обновление политики (только tax_rate)."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для частичного обновления"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 100.00,
            "markup_percent": 10.00,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    # Обновляем только tax_rate
    response = await authorized_client.put(
        f"/category-pricing-policy/{policy_id}",
        json={
            "tax_rate": 30.00,
        },
    )

    assert response.status_code == 200
    body = response.json()
    policy = CategoryPricingPolicyReadSchema(**body["data"])
    assert policy.tax_rate == 30.00
    # Остальные поля должны сохраниться
    assert policy.markup_fixed == 100.00
    assert policy.markup_percent == 10.00


@pytest.mark.asyncio
async def test_update_pricing_policy_200_set_null(authorized_client):
    """Успешное обнуление полей политики."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для обнуления"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 100.00,
            "markup_percent": 10.00,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    # Обнуляем markup_fixed (явно передаём null)
    response = await authorized_client.put(
        f"/category-pricing-policy/{policy_id}",
        json={
            "markup_fixed": None,
        },
    )

    assert response.status_code == 200
    body = response.json()
    # Проверяем, что значение в ответе None
    assert body["data"]["markup_fixed"] is None


@pytest.mark.asyncio
async def test_update_pricing_policy_404_not_found(authorized_client):
    """Ошибка при обновлении несуществующей политики."""
    response = await authorized_client.put(
        "/category-pricing-policy/999999",
        json={
            "tax_rate": 25.00,
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_not_found"


@pytest.mark.asyncio
async def test_update_pricing_policy_400_invalid_markup_percent(authorized_client):
    """Ошибка при обновлении с некорректным markup_percent."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    response = await authorized_client.put(
        f"/category-pricing-policy/{policy_id}",
        json={
            "markup_percent": 150.00,  # > 100
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_invalid_rate_value"


@pytest.mark.asyncio
async def test_update_pricing_policy_400_negative_tax_rate(authorized_client):
    """Ошибка при обновлении с отрицательным tax_rate."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    response = await authorized_client.put(
        f"/category-pricing-policy/{policy_id}",
        json={
            "tax_rate": -10.00,  # < 0
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_invalid_rate_value"


@pytest.mark.asyncio
async def test_update_pricing_policy_400_invalid_commission_percent(authorized_client):
    """Ошибка при обновлении с commission_percent > 100."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    response = await authorized_client.put(
        f"/category-pricing-policy/{policy_id}",
        json={
            "commission_percent": 110.00,  # > 100
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_invalid_rate_value"


@pytest.mark.asyncio
async def test_update_pricing_policy_403_no_permission(client):
    """Ошибка при обновлении без прав доступа (неавторизованный)."""
    response = await client.put(
        "/category-pricing-policy/1",
        json={
            "tax_rate": 25.00,
        },
    )

    # Без токена получаем 401, а не 403
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_pricing_policy_200_boundary_zero(authorized_client):
    """Обновление с нулевыми значениями."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_percent": 50.00,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    response = await authorized_client.put(
        f"/category-pricing-policy/{policy_id}",
        json={
            "markup_percent": 0.00,  # Граничное значение
            "tax_rate": 0.00,
        },
    )

    assert response.status_code == 200
    body = response.json()
    policy = CategoryPricingPolicyReadSchema(**body["data"])
    assert policy.markup_percent == 0.00
    assert policy.tax_rate == 0.00


@pytest.mark.asyncio
async def test_update_pricing_policy_200_boundary_hundred(authorized_client):
    """Обновление со значениями 100."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    create_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 20.00,
        },
    )
    assert create_response.status_code == 200
    policy_id = create_response.json()["data"]["id"]

    response = await authorized_client.put(
        f"/category-pricing-policy/{policy_id}",
        json={
            "markup_percent": 100.00,  # Максимальное значение
            "commission_percent": 100.00,
            "discount_percent": 100.00,
            "tax_rate": 100.00,
        },
    )

    assert response.status_code == 200
    body = response.json()
    policy = CategoryPricingPolicyReadSchema(**body["data"])
    assert policy.markup_percent == 100.00
    assert policy.commission_percent == 100.00
    assert policy.discount_percent == 100.00
    assert policy.tax_rate == 100.00
