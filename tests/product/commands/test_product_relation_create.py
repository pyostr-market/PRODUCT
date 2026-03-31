"""Тесты для команд управления связями товаров."""

import pytest

from src.catalog.product.api.schemas.schemas import ProductRelationReadSchema


@pytest.mark.asyncio
async def test_create_product_relation_200(authorized_client, test_products):
    """Успешное создание связи между товарами."""
    product_id = test_products[0]["id"]
    related_product_id = test_products[1]["id"]

    response = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    relation = ProductRelationReadSchema(**body["data"])
    assert relation.product_id == product_id
    assert relation.related_product_id == related_product_id
    assert relation.relation_type == "accessory"
    assert relation.sort_order == 1


@pytest.mark.asyncio
async def test_create_product_relation_similar_type(authorized_client, test_products):
    """Создание связи типа 'similar'."""
    product_id = test_products[0]["id"]
    related_product_id = test_products[1]["id"]

    response = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "similar",
            "sort_order": 0,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["relation_type"] == "similar"


@pytest.mark.asyncio
async def test_create_product_relation_bundle_type(authorized_client, test_products):
    """Создание связи типа 'bundle'."""
    product_id = test_products[0]["id"]
    related_product_id = test_products[1]["id"]

    response = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "bundle",
            "sort_order": 5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["relation_type"] == "bundle"
    assert body["data"]["sort_order"] == 5


@pytest.mark.asyncio
async def test_create_product_relation_upsell_type(authorized_client, test_products):
    """Создание связи типа 'upsell'."""
    product_id = test_products[0]["id"]
    related_product_id = test_products[1]["id"]

    response = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "upsell",
            "sort_order": 10,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["relation_type"] == "upsell"


@pytest.mark.asyncio
async def test_create_product_relation_self_reference_400(authorized_client, test_products):
    """Ошибка при попытке создать связь товара с самим собой."""
    product_id = test_products[0]["id"]

    response = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": product_id,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert "error" in body
    assert "self_reference" in body["error"]["code"]


@pytest.mark.asyncio
async def test_create_product_relation_duplicate_409(authorized_client, test_products):
    """Ошибка при попытке создать дублирующуюся связь."""
    product_id = test_products[0]["id"]
    related_product_id = test_products[1]["id"]

    # Создаём первую связь
    response1 = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )
    assert response1.status_code == 200

    # Пытаемся создать такую же связь
    response2 = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "accessory",
            "sort_order": 2,
        },
    )

    assert response2.status_code == 409
    body = response2.json()
    assert "error" in body
    assert "already_exists" in body["error"]["code"]


@pytest.mark.asyncio
async def test_create_product_relation_different_type_allowed(authorized_client, test_products):
    """Разрешено создание связей с разными типами для одной пары товаров."""
    product_id = test_products[0]["id"]
    related_product_id = test_products[1]["id"]

    # Создаём связь типа accessory
    response1 = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )
    assert response1.status_code == 200

    # Создаём связь типа similar для той же пары
    response2 = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "similar",
            "sort_order": 2,
        },
    )

    assert response2.status_code == 200
    body = response2.json()
    assert body["data"]["relation_type"] == "similar"


@pytest.mark.asyncio
async def test_create_product_relation_invalid_product_400(authorized_client):
    """Ошибка при создании связи с несуществующим товаром."""
    response = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": 99999,
            "related_product_id": 1,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_product_relation_invalid_related_product_400(authorized_client, test_products):
    """Ошибка при создании связи с несуществующим связанным товаром."""
    product_id = test_products[0]["id"]

    response = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": 99999,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_product_relation_zero_sort_order(authorized_client, test_products):
    """Создание связи с sort_order = 0 (значение по умолчанию)."""
    product_id = test_products[0]["id"]
    related_product_id = test_products[1]["id"]

    response = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "accessory",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["sort_order"] == 0


@pytest.mark.asyncio
async def test_create_product_relation_large_sort_order(authorized_client, test_products):
    """Создание связи с большим значением sort_order."""
    product_id = test_products[0]["id"]
    related_product_id = test_products[1]["id"]

    response = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_product_id,
            "relation_type": "accessory",
            "sort_order": 1000,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["sort_order"] == 1000


@pytest.mark.asyncio
async def test_create_product_relation_unauthorized(client):
    """Ошибка при создании связи без авторизации."""
    response = await client.post(
        "/product/product-relations",
        json={
            "product_id": 1,
            "related_product_id": 2,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_product_relation_no_permission(authorized_client_no_perms):
    """Ошибка при создании связи без нужного permission."""
    # Примечание: этот тест требует наличия товаров в БД
    # Для простоты проверяем только, что endpoint возвращает 403 без нужного permission
    response = await authorized_client_no_perms.post(
        "/product/product-relations",
        json={
            "product_id": 1,
            "related_product_id": 2,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )

    assert response.status_code == 403
