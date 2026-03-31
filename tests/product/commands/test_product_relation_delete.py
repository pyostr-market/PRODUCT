"""Тесты для команды удаления связи товаров."""

import pytest


@pytest.mark.asyncio
async def test_delete_product_relation_200(authorized_client, test_products, product_relation):
    """Успешное удаление связи товара."""
    relation_id = product_relation["id"]

    response = await authorized_client.delete(
        f"/product/product-relations/{relation_id}",
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_delete_product_relation_not_found(authorized_client):
    """Ошибка при удалении несуществующей связи."""
    response = await authorized_client.delete(
        "/product/product-relations/99999",
    )

    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert "not_found" in body["error"]["code"]


@pytest.mark.asyncio
async def test_delete_product_relation_already_deleted(authorized_client, test_products, product_relation):
    """Повторное удаление уже удалённой связи."""
    relation_id = product_relation["id"]

    # Первое удаление
    response1 = await authorized_client.delete(
        f"/product/product-relations/{relation_id}",
    )
    assert response1.status_code == 200

    # Повторное удаление
    response2 = await authorized_client.delete(
        f"/product/product-relations/{relation_id}",
    )

    assert response2.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_relation_unauthorized(client, product_relation):
    """Ошибка при удалении без авторизации."""
    relation_id = product_relation["id"]

    response = await client.delete(
        f"/product/product-relations/{relation_id}",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_product_relation_no_permission(authorized_client_no_perms, product_relation):
    """Ошибка при удалении без нужного permission."""
    relation_id = product_relation["id"]

    response = await authorized_client_no_perms.delete(
        f"/product/product-relations/{relation_id}",
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_product_relation_verify_removed(authorized_client, test_products, product_relation):
    """Проверка, что связь действительно удалена из БД."""
    relation_id = product_relation["id"]

    # Удаляем связь
    await authorized_client.delete(
        f"/product/product-relations/{relation_id}",
    )

    # Пытаемся получить связи товара
    product_id = product_relation["product_id"]
    get_response = await authorized_client.get(
        f"/product/products/{product_id}/relations",
    )

    assert get_response.status_code == 200
    body = get_response.json()
    
    # Удалённая связь не должна быть в списке
    items = body["data"]["items"]
    assert not any(item["id"] == relation_id for item in items)


@pytest.mark.asyncio
async def test_delete_product_relation_cascade_on_product_delete(
    authorized_client, 
    test_products, 
    product_relation
):
    """Проверка каскадного удаления связей при удалении товара."""
    relation_id = product_relation["id"]
    product_id = product_relation["product_id"]

    # Удаляем товар
    await authorized_client.delete(f"/product/{product_id}")

    # Проверяем, что связь тоже удалена
    get_response = await authorized_client.get(
        f"/product/products/{product_id}/relations",
    )

    assert get_response.status_code == 200
    body = get_response.json()
    items = body["data"]["items"]
    assert not any(item["id"] == relation_id for item in items)


@pytest.mark.asyncio
async def test_delete_one_of_many_relations(authorized_client, test_products):
    """Удаление одной связи из нескольких."""
    product_id = test_products[0]["id"]
    related_id_1 = test_products[1]["id"]
    related_id_2 = test_products[2]["id"]

    # Создаём две связи
    response1 = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_id_1,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )
    relation_id_1 = response1.json()["data"]["id"]

    response2 = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_id_2,
            "relation_type": "similar",
            "sort_order": 2,
        },
    )
    relation_id_2 = response2.json()["data"]["id"]

    # Удаляем первую связь
    delete_response = await authorized_client.delete(
        f"/product/product-relations/{relation_id_1}",
    )
    assert delete_response.status_code == 200

    # Проверяем, что вторая связь осталась
    get_response = await authorized_client.get(
        f"/product/products/{product_id}/relations",
    )
    assert get_response.status_code == 200
    body = get_response.json()
    items = body["data"]["items"]
    
    assert any(item["id"] == relation_id_2 for item in items)
    assert not any(item["id"] == relation_id_1 for item in items)


@pytest.mark.asyncio
async def test_delete_all_relations_for_product(authorized_client, test_products):
    """Удаление всех связей для товара."""
    product_id = test_products[0]["id"]
    related_id_1 = test_products[1]["id"]
    related_id_2 = test_products[2]["id"]

    # Создаём связи
    response1 = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_id_1,
            "relation_type": "accessory",
            "sort_order": 1,
        },
    )
    relation_id_1 = response1.json()["data"]["id"]

    response2 = await authorized_client.post(
        "/product/product-relations",
        json={
            "product_id": product_id,
            "related_product_id": related_id_2,
            "relation_type": "similar",
            "sort_order": 2,
        },
    )
    relation_id_2 = response2.json()["data"]["id"]

    # Удаляем обе связи
    await authorized_client.delete(f"/product/product-relations/{relation_id_1}")
    await authorized_client.delete(f"/product/product-relations/{relation_id_2}")

    # Проверяем, что связей нет
    get_response = await authorized_client.get(
        f"/product/products/{product_id}/relations",
    )
    assert get_response.status_code == 200
    body = get_response.json()
    assert body["data"]["items"] == []
    assert body["data"]["pagination"]["total"] == 0
