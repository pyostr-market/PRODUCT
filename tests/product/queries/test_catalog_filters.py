"""
Тесты для наследования device_type_id при получении фильтров каталога.

Проверяет, что если у категории не указан device_type_id,
он берётся из родительской категории.
"""

import json

import pytest


@pytest.mark.asyncio
async def test_catalog_filters_inherits_device_type_from_parent(authorized_client, client):
    """
    Проверяет наследование device_type_id от родительской категории.
    
    Сценарий:
    1. Создаём тип продукта "Smartphones"
    2. Создаём родительскую категорию "Mobile Devices" с device_type_id
    3. Создаём дочернюю категорию "Android Phones" БЕЗ device_type_id
    4. Создаём товар в дочерней категории с атрибутом "RAM"
    5. Запрашиваем фильтры для дочерней категории
    6. Проверяем, что фильтры возвращаются (наследуется device_type_id родителя)
    """
    # Создаём тип продукта
    product_type_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Smartphones"},
    )
    assert product_type_resp.status_code == 200
    product_type_id = product_type_resp.json()["data"]["id"]
    print(f"Created product_type: id={product_type_id}")

    # Создаём родительскую категорию с device_type_id
    parent_cat_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Mobile Devices",
            "device_type_id": product_type_id,
        },
    )
    assert parent_cat_resp.status_code == 200
    parent_category_id = parent_cat_resp.json()["data"]["id"]
    parent_device_type = parent_cat_resp.json()["data"].get("device_type")
    print(f"Created parent category: id={parent_category_id}, device_type={parent_device_type}")
    assert parent_device_type is not None, "У родительской категории должен быть device_type"
    assert parent_device_type["id"] == product_type_id

    # Создаём дочернюю категорию БЕЗ device_type_id
    child_cat_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Android Phones",
            "parent_id": parent_category_id,
            # device_type_id не указан - должен наследоваться
        },
    )
    assert child_cat_resp.status_code == 200
    child_category_id = child_cat_resp.json()["data"]["id"]
    child_parent = child_cat_resp.json()["data"].get("parent")
    print(f"Created child category: id={child_category_id}, parent={child_parent}")
    assert child_parent is not None, "У дочерней категории должен быть parent"
    assert child_parent["id"] == parent_category_id

    # Создаём товар в дочерней категории с атрибутами
    product_resp = await authorized_client.post(
        "/product",
        data={
            "name": "Test Android Phone",
            "price": "500.00",
            "category_id": str(child_category_id),
            "attributes_json": json.dumps([
                {"name": "RAM", "value": "8 GB", "is_filterable": True},
            ]),
        },
    )
    assert product_resp.status_code == 200
    product_id = product_resp.json()["data"]["id"]
    product_category = product_resp.json()["data"].get("category")
    product_attributes = product_resp.json()["data"].get("attributes", [])
    assert product_category is not None, "У товара должна быть категория"
    assert product_category["id"] == child_category_id
    assert len(product_attributes) > 0, "У товара должны быть атрибуты"

    # Запрашиваем фильтры для дочерней категории (без device_type_id)
    response = await client.get(f"/product/catalog/filters?category_id={child_category_id}")
    
    assert response.status_code == 200
    body = response.json()
    print(f"Response: {body}")
    
    # Проверяем, что фильтры вернулись
    assert "data" in body
    assert "filters" in body["data"]
    
    # Проверяем, что атрибут "RAM" присутствует в фильтрах
    filters = body["data"]["filters"]
    print(f"Filters: {filters}")
    ram_filter = next((f for f in filters if f["name"] == "RAM"), None)
    assert ram_filter is not None, "Атрибут RAM должен быть в фильтрах"
    assert ram_filter["is_filterable"] is True
    assert len(ram_filter["options"]) > 0


@pytest.mark.asyncio
async def test_catalog_filters_direct_device_type(authorized_client, client):
    """
    Проверяет работу с прямым указанием device_type_id в категории.
    
    Сценарий:
    1. Создаём тип продукта "Laptops"
    2. Создаём категорию "Laptops" с device_type_id
    3. Создаём товар с атрибутом "Screen Size"
    4. Запрашиваем фильтры для категории
    5. Проверяем, что фильтры возвращаются корректно
    """
    # Создаём тип продукта
    product_type_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Laptops"},
    )
    assert product_type_resp.status_code == 200
    product_type_id = product_type_resp.json()["data"]["id"]

    # Создаём категорию с device_type_id
    cat_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Laptops",
            "device_type_id": product_type_id,
        },
    )
    assert cat_resp.status_code == 200
    category_id = cat_resp.json()["data"]["id"]

    # Создаём товар с атрибутами
    product_resp = await authorized_client.post(
        "/product",
        data={
            "name": "Test Laptop",
            "price": "1000.00",
            "category_id": str(category_id),
            "attributes_json": json.dumps([
                {"name": "Screen Size", "value": "15.6 inches", "is_filterable": True},
            ]),
        },
    )
    assert product_resp.status_code == 200
    product_id = product_resp.json()["data"]["id"]
    assert len(product_resp.json()["data"].get("attributes", [])) > 0

    # Запрашиваем фильтры
    response = await client.get(f"/product/catalog/filters?category_id={category_id}")
    
    assert response.status_code == 200
    body = response.json()
    
    assert "data" in body
    assert "filters" in body["data"]
    
    filters = body["data"]["filters"]
    screen_filter = next((f for f in filters if f["name"] == "Screen Size"), None)
    assert screen_filter is not None, "Атрибут Screen Size должен быть в фильтрах"


@pytest.mark.asyncio
async def test_catalog_filters_nested_inheritance_chain(authorized_client, client):
    """
    Проверяет наследование device_type_id через несколько уровней вложенности.
    
    Сценарий:
    1. Создаём тип продукта "Tablets"
    2. Создаём цепочку: Electronics (с device_type) -> Mobile -> Tablets (без device_type)
    3. Создаём товар в конечной категории
    4. Проверяем, что фильтры работают с наследованием через 2 уровня
    """
    # Создаём тип продукта
    product_type_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Tablets"},
    )
    assert product_type_resp.status_code == 200
    product_type_id = product_type_resp.json()["data"]["id"]

    # Создаём корневую категорию с device_type_id
    root_cat_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Electronics",
            "device_type_id": product_type_id,
        },
    )
    assert root_cat_resp.status_code == 200
    root_category_id = root_cat_resp.json()["data"]["id"]

    # Создаём промежуточную категорию БЕЗ device_type_id
    middle_cat_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Mobile",
            "parent_id": root_category_id,
        },
    )
    assert middle_cat_resp.status_code == 200
    middle_category_id = middle_cat_resp.json()["data"]["id"]

    # Создаём конечную категорию БЕЗ device_type_id
    child_cat_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Tablets Category",
            "parent_id": middle_category_id,
        },
    )
    assert child_cat_resp.status_code == 200
    child_category_id = child_cat_resp.json()["data"]["id"]

    # Создаём товар в конечной категории с атрибутами
    import json
    product_resp = await authorized_client.post(
        "/product",
        data={
            "name": "Test Tablet",
            "price": "400.00",
            "category_id": str(child_category_id),
            "attributes_json": json.dumps([
                {"name": "Storage", "value": "128 GB", "is_filterable": True},
            ]),
        },
    )
    assert product_resp.status_code == 200
    product_id = product_resp.json()["data"]["id"]
    assert len(product_resp.json()["data"].get("attributes", [])) > 0

    # Запрашиваем фильтры для конечной категории
    response = await client.get(f"/product/catalog/filters?category_id={child_category_id}")
    
    assert response.status_code == 200
    body = response.json()
    
    assert "data" in body
    assert "filters" in body["data"]
    
    filters = body["data"]["filters"]
    storage_filter = next((f for f in filters if f["name"] == "Storage"), None)
    assert storage_filter is not None, "Атрибут Storage должен быть в фильтрах"


@pytest.mark.asyncio
async def test_catalog_filters_with_product_type_id_direct(authorized_client, client):
    """
    Проверяет работу с прямым указанием product_type_id (device_type_id).
    
    Сценарий:
    1. Создаём тип продукта "Cameras"
    2. Создаём товар с атрибутом "Megapixels"
    3. Запрашиваем фильтры по product_type_id
    4. Проверяем, что фильтры возвращаются
    """
    # Создаём тип продукта
    product_type_resp = await authorized_client.post(
        "/product/type",
        json={"name": "Cameras"},
    )
    assert product_type_resp.status_code == 200
    product_type_id = product_type_resp.json()["data"]["id"]

    # Создаём категорию с device_type_id
    cat_resp = await authorized_client.post(
        "/category",
        json={
            "name": "Cameras Category",
            "device_type_id": product_type_id,
        },
    )
    assert cat_resp.status_code == 200
    category_id = cat_resp.json()["data"]["id"]

    # Создаём товар с атрибутами
    import json
    product_resp = await authorized_client.post(
        "/product",
        data={
            "name": "Test Camera",
            "price": "600.00",
            "category_id": str(category_id),
            "attributes_json": json.dumps([
                {"name": "Megapixels", "value": "24 MP", "is_filterable": True},
            ]),
        },
    )
    assert product_resp.status_code == 200
    product_id = product_resp.json()["data"]["id"]
    assert len(product_resp.json()["data"].get("attributes", [])) > 0

    # Запрашиваем фильтры по product_type_id
    response = await client.get(f"/product/catalog/filters?device_type_id={product_type_id}")
    
    assert response.status_code == 200
    body = response.json()
    
    assert "data" in body
    assert "filters" in body["data"]
    
    filters = body["data"]["filters"]
    mp_filter = next((f for f in filters if f["name"] == "Megapixels"), None)
    assert mp_filter is not None, "Атрибут Megapixels должен быть в фильтрах"
