import pytest

from src.catalog.category.api.schemas.schemas import CategoryPricingPolicyReadSchema


@pytest.mark.asyncio
async def test_filter_pricing_policies_200_all(authorized_client):
    """Успешное получение всех политик ценообразования."""
    # Создаём несколько категорий с политиками
    category_ids = []
    for i in range(3):
        cat_response = await authorized_client.post(
            "/category",
            data={"name": f"Категория {i}"},
        )
        assert cat_response.status_code == 200
        category_ids.append(cat_response.json()["data"]["id"])

        policy_response = await authorized_client.post(
            "/category-pricing-policy",
            json={
                "category_id": category_ids[-1],
                "markup_percent": 10.00 + i * 5,
                "tax_rate": 20.00,
            },
        )
        assert policy_response.status_code == 200

    # Получаем все политики
    response = await authorized_client.get(
        "/category-pricing-policy",
        params={"limit": 10, "offset": 0},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 3
    assert len(body["data"]["items"]) == 3


@pytest.mark.asyncio
async def test_filter_pricing_policies_200_by_category_id(authorized_client):
    """Фильтрация политик по category_id."""
    # Создаём категории с политиками
    category_ids = []
    for i in range(3):
        cat_response = await authorized_client.post(
            "/category",
            data={"name": f"Категория {i}"},
        )
        assert cat_response.status_code == 200
        category_ids.append(cat_response.json()["data"]["id"])

        policy_response = await authorized_client.post(
            "/category-pricing-policy",
            json={
                "category_id": category_ids[-1],
                "markup_percent": 10.00 + i * 5,
                "tax_rate": 20.00,
            },
        )
        assert policy_response.status_code == 200

    # Фильтруем по первой категории
    response = await authorized_client.get(
        "/category-pricing-policy",
        params={"category_id": category_ids[0], "limit": 10, "offset": 0},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert len(body["data"]["items"]) == 1
    assert body["data"]["items"][0]["category_id"] == category_ids[0]


@pytest.mark.asyncio
async def test_filter_pricing_policies_200_pagination(authorized_client):
    """Проверка пагинации при фильтрации."""
    # Создаём 5 категорий с политиками
    category_ids = []
    for i in range(5):
        cat_response = await authorized_client.post(
            "/category",
            data={"name": f"Категория {i}"},
        )
        assert cat_response.status_code == 200
        category_ids.append(cat_response.json()["data"]["id"])

        policy_response = await authorized_client.post(
            "/category-pricing-policy",
            json={
                "category_id": category_ids[-1],
                "markup_percent": 10.00,
                "tax_rate": 20.00,
            },
        )
        assert policy_response.status_code == 200

    # Получаем первые 2 записи
    response1 = await authorized_client.get(
        "/category-pricing-policy",
        params={"limit": 2, "offset": 0},
    )
    assert response1.status_code == 200
    body1 = response1.json()
    assert body1["data"]["total"] == 5
    assert len(body1["data"]["items"]) == 2

    # Получаем следующие 2 записи
    response2 = await authorized_client.get(
        "/category-pricing-policy",
        params={"limit": 2, "offset": 2},
    )
    assert response2.status_code == 200
    body2 = response2.json()
    assert body2["data"]["total"] == 5
    assert len(body2["data"]["items"]) == 2

    # Получаем последнюю запись
    response3 = await authorized_client.get(
        "/category-pricing-policy",
        params={"limit": 2, "offset": 4},
    )
    assert response3.status_code == 200
    body3 = response3.json()
    assert body3["data"]["total"] == 5
    assert len(body3["data"]["items"]) == 1


@pytest.mark.asyncio
async def test_filter_pricing_policies_200_empty_result(authorized_client):
    """Фильтрация с пустым результатом."""
    # Фильтруем по несуществующей категории
    response = await authorized_client.get(
        "/category-pricing-policy",
        params={"category_id": 999999, "limit": 10, "offset": 0},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 0
    assert len(body["data"]["items"]) == 0


@pytest.mark.asyncio
async def test_filter_pricing_policies_200_limit_max(authorized_client):
    """Проверка максимального limit (100)."""
    response = await authorized_client.get(
        "/category-pricing-policy",
        params={"limit": 100, "offset": 0},
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_filter_pricing_policy_403_no_permission(client):
    """Ошибка при фильтрации без прав доступа (неавторизованный)."""
    response = await client.get(
        "/category-pricing-policy",
        params={"limit": 10, "offset": 0},
    )

    # Без токена получаем 401, а не 403
    assert response.status_code == 401
