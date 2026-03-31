"""Тесты для команды обновления связи товаров."""

import pytest

from src.catalog.product.api.schemas.schemas import ProductRelationReadSchema


@pytest.mark.asyncio
async def test_update_product_relation_200(authorized_client, test_products, product_relation):
    """Успешное обновление связи товара."""
    relation_id = product_relation["id"]

    response = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={
            "relation_type": "similar",
            "sort_order": 10,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    relation = ProductRelationReadSchema(**body["data"])
    assert relation.id == relation_id
    assert relation.relation_type == "similar"
    assert relation.sort_order == 10


@pytest.mark.asyncio
async def test_update_product_relation_only_type(authorized_client, test_products, product_relation):
    """Обновление только типа связи."""
    relation_id = product_relation["id"]
    old_sort_order = product_relation["sort_order"]

    response = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={
            "relation_type": "bundle",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["data"]["relation_type"] == "bundle"
    assert body["data"]["sort_order"] == old_sort_order


@pytest.mark.asyncio
async def test_update_product_relation_only_sort_order(authorized_client, test_products, product_relation):
    """Обновление только порядка сортировки."""
    relation_id = product_relation["id"]
    old_relation_type = product_relation["relation_type"]

    response = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={
            "sort_order": 99,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["data"]["relation_type"] == old_relation_type
    assert body["data"]["sort_order"] == 99


@pytest.mark.asyncio
async def test_update_product_relation_empty_body(authorized_client, product_relation):
    """Обновление с пустым телом (ничего не меняется)."""
    relation_id = product_relation["id"]
    old_relation_type = product_relation["relation_type"]
    old_sort_order = product_relation["sort_order"]

    response = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["data"]["relation_type"] == old_relation_type
    assert body["data"]["sort_order"] == old_sort_order


@pytest.mark.asyncio
async def test_update_product_relation_not_found(authorized_client):
    """Ошибка при обновлении несуществующей связи."""
    response = await authorized_client.put(
        "/product/product-relations/99999",
        json={
            "relation_type": "similar",
            "sort_order": 1,
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert "not_found" in body["error"]["code"]


@pytest.mark.asyncio
async def test_update_product_relation_to_accessory(authorized_client, test_products, product_relation):
    """Обновление типа связи на 'accessory'."""
    relation_id = product_relation["id"]

    response = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={
            "relation_type": "accessory",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["relation_type"] == "accessory"


@pytest.mark.asyncio
async def test_update_product_relation_to_upsell(authorized_client, test_products, product_relation):
    """Обновление типа связи на 'upsell'."""
    relation_id = product_relation["id"]

    response = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={
            "relation_type": "upsell",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["relation_type"] == "upsell"


@pytest.mark.asyncio
async def test_update_product_relation_sort_order_zero(authorized_client, test_products, product_relation):
    """Обновление sort_order на 0."""
    relation_id = product_relation["id"]

    response = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={
            "sort_order": 0,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["sort_order"] == 0


@pytest.mark.asyncio
async def test_update_product_relation_sort_order_negative(authorized_client, test_products, product_relation):
    """Обновление sort_order на отрицательное значение."""
    relation_id = product_relation["id"]

    response = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={
            "sort_order": -5,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["sort_order"] == -5


@pytest.mark.asyncio
async def test_update_product_relation_unauthorized(client, product_relation):
    """Ошибка при обновлении без авторизации."""
    relation_id = product_relation["id"]

    response = await client.put(
        f"/product/product-relations/{relation_id}",
        json={
            "relation_type": "similar",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_product_relation_no_permission(authorized_client_no_perms, product_relation):
    """Ошибка при обновлении без нужного permission."""
    relation_id = product_relation["id"]

    response = await authorized_client_no_perms.put(
        f"/product/product-relations/{relation_id}",
        json={
            "relation_type": "similar",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_product_relation_preserves_product_ids(authorized_client, test_products, product_relation):
    """Обновление не меняет product_id и related_product_id."""
    relation_id = product_relation["id"]
    original_product_id = product_relation["product_id"]
    original_related_id = product_relation["related_product_id"]

    response = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={
            "relation_type": "similar",
            "sort_order": 50,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["product_id"] == original_product_id
    assert body["data"]["related_product_id"] == original_related_id


@pytest.mark.asyncio
async def test_update_product_relation_multiple_times(authorized_client, test_products, product_relation):
    """Многократное обновление связи."""
    relation_id = product_relation["id"]

    # Первое обновление
    response1 = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={"relation_type": "similar", "sort_order": 5},
    )
    assert response1.status_code == 200
    assert response1.json()["data"]["relation_type"] == "similar"

    # Второе обновление
    response2 = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={"relation_type": "bundle", "sort_order": 10},
    )
    assert response2.status_code == 200
    assert response2.json()["data"]["relation_type"] == "bundle"
    assert response2.json()["data"]["sort_order"] == 10

    # Третье обновление
    response3 = await authorized_client.put(
        f"/product/product-relations/{relation_id}",
        json={"sort_order": 15},
    )
    assert response3.status_code == 200
    assert response3.json()["data"]["relation_type"] == "bundle"
    assert response3.json()["data"]["sort_order"] == 15
