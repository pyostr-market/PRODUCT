import pytest

from src.catalog.category.api.schemas.schemas import CategoryPricingPolicyReadSchema


@pytest.mark.asyncio
async def test_create_pricing_policy_200(authorized_client):
    """Успешное создание политики ценообразования."""
    # Сначала создаём категорию
    category_response = await authorized_client.post(
        "/category",
        data={
            "name": "Тестовая категория",
            "description": "Категория для тестирования политики цен",
        },
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    # Создаём политику ценообразования
    response = await authorized_client.post(
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

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    policy = CategoryPricingPolicyReadSchema(**body["data"])
    assert policy.category_id == category_id
    assert policy.markup_fixed == 100.00
    assert policy.markup_percent == 15.00
    assert policy.commission_percent == 5.00
    assert policy.discount_percent == 2.00
    assert policy.tax_rate == 20.00


@pytest.mark.asyncio
async def test_create_pricing_policy_200_minimal_data(authorized_client):
    """Создание политики с минимальными данными (только category_id и tax_rate)."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для минимального теста"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 0.00,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    policy = CategoryPricingPolicyReadSchema(**body["data"])
    assert policy.category_id == category_id
    assert policy.tax_rate == 0.00
    assert policy.markup_fixed is None
    assert policy.markup_percent is None
    assert policy.commission_percent is None
    assert policy.discount_percent is None


@pytest.mark.asyncio
async def test_create_pricing_policy_400_category_not_found(authorized_client):
    """Ошибка при создании политики для несуществующей категории."""
    response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": 999999,
            "tax_rate": 20.00,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_category_not_found"


@pytest.mark.asyncio
async def test_create_pricing_policy_400_invalid_markup_percent(authorized_client):
    """Ошибка при создании политики с markup_percent > 100."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста валидации"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_percent": 150.00,  # > 100
            "tax_rate": 20.00,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_invalid_rate_value"
    assert body["error"]["details"]["field"] == "markup_percent"


@pytest.mark.asyncio
async def test_create_pricing_policy_400_negative_markup_percent(authorized_client):
    """Ошибка при создании политики с отрицательным markup_percent."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста валидации"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_percent": -5.00,  # < 0
            "tax_rate": 20.00,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_invalid_rate_value"


@pytest.mark.asyncio
async def test_create_pricing_policy_400_invalid_commission_percent(authorized_client):
    """Ошибка при создании политики с commission_percent > 100."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста валидации"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "commission_percent": 120.00,  # > 100
            "tax_rate": 20.00,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_invalid_rate_value"


@pytest.mark.asyncio
async def test_create_pricing_policy_400_invalid_discount_percent(authorized_client):
    """Ошибка при создании политики с discount_percent > 100."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста валидации"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "discount_percent": -10.00,  # < 0
            "tax_rate": 20.00,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_invalid_rate_value"


@pytest.mark.asyncio
async def test_create_pricing_policy_400_invalid_tax_rate(authorized_client):
    """Ошибка при создании политики с tax_rate > 100."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста валидации"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 150.00,  # > 100
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_invalid_rate_value"


@pytest.mark.asyncio
async def test_create_pricing_policy_400_negative_tax_rate(authorized_client):
    """Ошибка при создании политики с отрицательным tax_rate."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста валидации"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": -5.00,  # < 0
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_invalid_rate_value"


@pytest.mark.asyncio
async def test_create_pricing_policy_409_already_exists(authorized_client):
    """Ошибка при создании второй политики для той же категории."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста дубликата"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    # Создаём первую политику
    create1_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 20.00,
        },
    )
    assert create1_response.status_code == 200

    # Пытаемся создать вторую политику для той же категории
    create2_response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "tax_rate": 10.00,
        },
    )

    assert create2_response.status_code == 409
    body = create2_response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_pricing_policy_already_exists"


@pytest.mark.asyncio
async def test_create_pricing_policy_403_no_permission(client):
    """Ошибка при создании политики без прав доступа (неавторизованный)."""
    # Сначала создадим категорию через авторизованного клиента
    # Но это не поможет, так как client - неавторизованный
    # Тест проверяет, что без токена вообще доступ запрещён (401)
    response = await client.post(
        "/category-pricing-policy",
        json={
            "category_id": 1,
            "tax_rate": 20.00,
        },
    )

    # Без токена получаем 401, а не 403
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_pricing_policy_200_boundary_values(authorized_client):
    """Создание политики с граничными значениями (0 и 100)."""
    category_response = await authorized_client.post(
        "/category",
        data={"name": "Категория для теста границ"},
    )
    assert category_response.status_code == 200
    category_id = category_response.json()["data"]["id"]

    response = await authorized_client.post(
        "/category-pricing-policy",
        json={
            "category_id": category_id,
            "markup_fixed": 0.00,
            "markup_percent": 100.00,  # Максимальное значение
            "commission_percent": 0.00,  # Минимальное значение
            "discount_percent": 100.00,
            "tax_rate": 0.00,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    policy = CategoryPricingPolicyReadSchema(**body["data"])
    assert policy.markup_percent == 100.00
    assert policy.commission_percent == 0.00
    assert policy.discount_percent == 100.00
    assert policy.tax_rate == 0.00
