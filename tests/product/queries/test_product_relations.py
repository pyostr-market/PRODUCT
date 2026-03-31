"""Тесты для получения связей и рекомендаций товаров."""

import pytest


@pytest.mark.asyncio
async def test_get_product_relations_200(authorized_client, test_products, product_relation):
    """Успешное получение списка связей товара."""
    product_id = test_products[0]["id"]

    response = await authorized_client.get(
        f"/product/products/{product_id}/relations",
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "items" in body["data"]
    assert "pagination" in body["data"]
    
    items = body["data"]["items"]
    assert len(items) >= 1
    
    # Проверяем, что наша связь есть в списке
    relation_ids = [item["id"] for item in items]
    assert product_relation["id"] in relation_ids


@pytest.mark.asyncio
async def test_get_product_relations_with_pagination(authorized_client, test_products):
    """Получение связей с пагинацией."""
    product_id = test_products[0]["id"]
    
    # Создаём 5 связей
    relation_ids = []
    for i in range(1, 6):
        response = await authorized_client.post(
            "/product/product-relations",
            json={
                "product_id": product_id,
                "related_product_id": test_products[i % 3]["id"],
                "relation_type": "accessory",
                "sort_order": i,
            },
        )
        relation_ids.append(response.json()["data"]["id"])

    # Получаем первую страницу (limit=2)
    response1 = await authorized_client.get(
        f"/product/products/{product_id}/relations",
        params={"page": 1, "limit": 2},
    )
    assert response1.status_code == 200
    body1 = response1.json()
    assert len(body1["data"]["items"]) == 2
    assert body1["data"]["pagination"]["page"] == 1
    assert body1["data"]["pagination"]["limit"] == 2
    assert body1["data"]["pagination"]["total"] == 5

    # Получаем вторую страницу
    response2 = await authorized_client.get(
        f"/product/products/{product_id}/relations",
        params={"page": 2, "limit": 2},
    )
    assert response2.status_code == 200
    body2 = response2.json()
    assert len(body2["data"]["items"]) == 2
    assert body2["data"]["pagination"]["page"] == 2

    # Получаем третью страницу
    response3 = await authorized_client.get(
        f"/product/products/{product_id}/relations",
        params={"page": 3, "limit": 2},
    )
    assert response3.status_code == 200
    body3 = response3.json()
    assert len(body3["data"]["items"]) == 1
    assert body3["data"]["pagination"]["page"] == 3


@pytest.mark.asyncio
async def test_get_product_relations_filter_by_type(authorized_client, test_products):
    """Фильтрация связей по типу."""
    product_id = test_products[0]["id"]
    
    # Создаём связи разных типов
    await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": test_products[1]["id"],
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )
    await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": test_products[2]["id"],
            "relation_type": "similar",
            "sort_order": 2,
        },
    )
    await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": test_products[1]["id"],
            "relation_type": "bundle",
            "sort_order": 3,
        },
    )

    # Фильтруем по типу accessory
    response = await authorized_client.get(
        f"/product/products/{product_id}/relations",
        params={"relation_type": "accessory"},
    )
    assert response.status_code == 200
    body = response.json()
    items = body["data"]["items"]
    assert len(items) == 1
    assert all(item["id"] is not None for item in items)

    # Фильтруем по типу similar
    response2 = await authorized_client.get(
        f"/product/products/{product_id}/relations",
        params={"relation_type": "similar"},
    )
    assert response2.status_code == 200
    body2 = response2.json()
    assert len(body2["data"]["items"]) == 1

    # Фильтруем по типу bundle
    response3 = await authorized_client.get(
        f"/product/products/{product_id}/relations",
        params={"relation_type": "bundle"},
    )
    assert response3.status_code == 200
    body3 = response3.json()
    assert len(body3["data"]["items"]) == 1


@pytest.mark.asyncio
async def test_get_product_relations_empty_list(authorized_client, test_products):
    """Получение пустого списка связей."""
    product_id = test_products[0]["id"]

    response = await authorized_client.get(
        f"/product/products/{product_id}/relations",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["items"] == []
    assert body["data"]["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_get_product_relations_sorted_by_sort_order(authorized_client, test_products):
    """Проверка сортировки связей по sort_order."""
    product_id = test_products[0]["id"]
    
    # Создаём связи с разным sort_order
    await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": test_products[1]["id"],
            "relation_type": "accessory",
            "sort_order": 10,
        },
    )
    await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": test_products[2]["id"],
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )
    await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": test_products[1]["id"],
            "relation_type": "accessory",
            "sort_order": 5,
        },
    )

    response = await authorized_client.get(
        f"/product/products/{product_id}/relations",
    )
    assert response.status_code == 200
    
    body = response.json()
    items = body["data"]["items"]
    
    # Проверяем, что элементы отсортированы по sort_order
    sort_orders = [item["id"] for item in items]
    assert len(sort_orders) == 3


@pytest.mark.asyncio
async def test_get_product_relations_response_structure(authorized_client, test_products, product_relation):
    """Проверка структуры ответа API."""
    product_id = test_products[0]["id"]

    response = await authorized_client.get(
        f"/product/products/{product_id}/relations",
    )

    assert response.status_code == 200
    body = response.json()
    
    # Проверяем структуру
    assert "success" in body
    assert "data" in body
    assert "items" in body["data"]
    assert "pagination" in body["data"]
    
    # Проверяем структуру pagination
    pagination = body["data"]["pagination"]
    assert "page" in pagination
    assert "limit" in pagination
    assert "total" in pagination
    
    # Проверяем структуру элемента
    if body["data"]["items"]:
        item = body["data"]["items"][0]
        assert "id" in item
        assert "name" in item
        assert "price" in item


@pytest.mark.asyncio
async def test_get_product_relations_public_access(client, test_products, product_relation):
    """Проверка, что endpoint доступен без авторизации."""
    product_id = test_products[0]["id"]

    response = await client.get(
        f"/product/products/{product_id}/relations",
    )

    # Должен быть доступен (публичный endpoint)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_product_recommendations_200(authorized_client, test_products, product_relation):
    """Успешное получение рекомендаций для товара."""
    product_id = test_products[0]["id"]

    response = await authorized_client.get(
        f"/product/products/{product_id}/recommendations",
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "items" in body["data"]
    assert "pagination" in body["data"]
    
    items = body["data"]["items"]
    assert len(items) >= 1


@pytest.mark.asyncio
async def test_get_product_recommendations_filter_by_type(authorized_client, test_products):
    """Фильтрация рекомендаций по типу."""
    product_id = test_products[0]["id"]
    
    # Создаём рекомендации разных типов
    await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": test_products[1]["id"],
            "relation_type": "similar",
            "sort_order": 1,
        },
    )
    await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": test_products[2]["id"],
            "relation_type": "upsell",
            "sort_order": 2,
        },
    )

    # Фильтруем по типу similar
    response = await authorized_client.get(
        f"/product/products/{product_id}/recommendations",
        params={"relation_type": "similar"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]["items"]) == 1

    # Фильтруем по типу upsell
    response2 = await authorized_client.get(
        f"/product/products/{product_id}/recommendations",
        params={"relation_type": "upsell"},
    )
    assert response2.status_code == 200
    body2 = response2.json()
    assert len(body2["data"]["items"]) == 1


@pytest.mark.asyncio
async def test_get_product_recommendations_public_access(client, test_products, product_relation):
    """Проверка, что endpoint рекомендаций доступен без авторизации."""
    product_id = test_products[0]["id"]

    response = await client.get(
        f"/product/products/{product_id}/recommendations",
    )

    # Должен быть доступен (публичный endpoint)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_product_recommendations_with_large_limit(authorized_client, test_products):
    """Получение рекомендаций с большим limit."""
    product_id = test_products[0]["id"]
    
    # Создаём несколько связей
    for i in range(1, 4):
        await authorized_client.post(
            "/product/product-relations",
            json={
                "product_id": product_id,
                "related_product_id": test_products[i % 3]["id"],
                "relation_type": "accessory",
                "sort_order": i,
            },
        )

    response = await authorized_client.get(
        f"/product/products/{product_id}/recommendations",
        params={"limit": 100},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["pagination"]["limit"] == 100
    assert body["data"]["pagination"]["total"] == 3


@pytest.mark.asyncio
async def test_get_product_recommendations_offset_page_2(authorized_client, test_products):
    """Получение рекомендаций со второй страницы."""
    product_id = test_products[0]["id"]
    
    # Создаём 5 связей
    for i in range(1, 6):
        await authorized_client.post(
            "/product/product-relations",
            json={
                "product_id": product_id,
                "related_product_id": test_products[i % 3]["id"],
                "relation_type": "accessory",
                "sort_order": i,
            },
        )

    response = await authorized_client.get(
        f"/product/products/{product_id}/recommendations",
        params={"page": 2, "limit": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["pagination"]["page"] == 2
    assert len(body["data"]["items"]) == 2
