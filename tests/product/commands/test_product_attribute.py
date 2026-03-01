import pytest

from src.catalog.product.api.schemas.schemas import ProductAttributeReadSchema


@pytest.mark.asyncio
async def test_create_product_attribute_200(authorized_client):
    """Создать атрибут продукта"""
    response = await authorized_client.post(
        "/product/attribute",
        json={"name": "Color", "value": "Black", "is_filterable": True}
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert "data" in body

    attr = ProductAttributeReadSchema(**body["data"])
    assert attr.name == "Color"
    assert attr.value == "Black"
    assert attr.is_filterable is True


@pytest.mark.asyncio
async def test_create_product_attribute_default_is_filterable(authorized_client):
    """Атрибут создаётся с is_filterable=False по умолчанию"""
    response = await authorized_client.post(
        "/product/attribute",
        json={"name": "Weight", "value": "100g"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["is_filterable"] is False


@pytest.mark.asyncio
async def test_update_product_attribute_200(authorized_client):
    """Обновить атрибут продукта"""
    # Создаём
    create = await authorized_client.post(
        "/product/attribute",
        json={"name": "OldName", "value": "OldValue", "is_filterable": False}
    )
    attr_id = create.json()["data"]["id"]

    # Обновляем
    response = await authorized_client.put(
        f"/product/attribute/{attr_id}",
        json={"name": "NewName", "value": "NewValue", "is_filterable": True}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["name"] == "NewName"
    assert body["data"]["value"] == "NewValue"
    assert body["data"]["is_filterable"] is True


@pytest.mark.asyncio
async def test_update_product_attribute_partial(authorized_client):
    """Частичное обновление атрибута"""
    create = await authorized_client.post(
        "/product/attribute",
        json={"name": "Color", "value": "Red", "is_filterable": False}
    )
    attr_id = create.json()["data"]["id"]

    # Обновляем только значение
    response = await authorized_client.put(
        f"/product/attribute/{attr_id}",
        json={"value": "Blue"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["name"] == "Color"  # не изменилось
    assert body["data"]["value"] == "Blue"


@pytest.mark.asyncio
async def test_update_product_attribute_404(authorized_client):
    """Обновление несуществующего атрибута"""
    response = await authorized_client.put(
        "/product/attribute/99999",
        json={"name": "New Name", "value": "New Value"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_product_attribute_200(authorized_client):
    """Удалить атрибут продукта"""
    # Создаём
    create = await authorized_client.post(
        "/product/attribute",
        json={"name": "To Delete", "value": "Value", "is_filterable": False}
    )
    attr_id = create.json()["data"]["id"]

    # Удаляем
    response = await authorized_client.delete(f"/product/attribute/{attr_id}")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_delete_product_attribute_404(authorized_client):
    """Удаление несуществующего атрибута"""
    response = await authorized_client.delete("/product/attribute/99999")
    assert response.status_code == 404
