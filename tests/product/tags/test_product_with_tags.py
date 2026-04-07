import json

import pytest

from src.catalog.product.api.schemas.schemas import (
    ProductReadSchema,
    ProductListResponse,
    TagReadSchema,
)


# ============================================================
# GET PRODUCT WITH TAGS
# ============================================================


@pytest.mark.asyncio
async def test_get_product_200_with_tags(authorized_client, product_with_tags):
    """Получение товара с тегами."""
    product_id = product_with_tags["product"]["id"]

    response = await authorized_client.get(f"/product/{product_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert product.id == product_id

    # Проверяем теги
    assert len(product.tags) == 2
    tag_names = {tag.name for tag in product.tags}
    assert "популярный" in tag_names
    assert "новинка" in tag_names

    # Проверяем структуру тегов
    for tag in product.tags:
        assert isinstance(tag.tag_id, int)
        assert isinstance(tag.name, str)
        # description может быть None
        assert tag.description is None or isinstance(tag.description, str)


@pytest.mark.asyncio
async def test_get_product_200_no_tags(authorized_client):
    """Получение товара без тегов — пустой массив."""
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Без тегов", "price": "100.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    response = await authorized_client.get(f"/product/{product_id}")

    assert response.status_code == 200
    body = response.json()
    product = ProductReadSchema(**body["data"])

    assert product.tags == []


@pytest.mark.asyncio
async def test_get_product_200_single_tag(authorized_client):
    """Получение товара с одним тегом."""
    # Создаём товар
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Один тег", "price": "250.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    # Создаём тег и привязываем
    tag_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "единый", "description": "Единственный тег"},
    )
    tag_id = tag_resp.json()["data"]["tag_id"]

    await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": tag_id},
    )

    response = await authorized_client.get(f"/product/{product_id}")

    assert response.status_code == 200
    body = response.json()
    product = ProductReadSchema(**body["data"])

    assert len(product.tags) == 1
    assert product.tags[0].name == "единый"
    assert product.tags[0].description == "Единственный тег"
    assert product.tags[0].tag_id == tag_id


# ============================================================
# PRODUCT LIST WITH TAGS
# ============================================================


@pytest.mark.asyncio
async def test_product_list_200_includes_tags(authorized_client):
    """Список товаров включает теги."""
    # Создаём 2 товара с разными тегами
    product_ids = []
    for i in range(2):
        resp = await authorized_client.post(
            "/product",
            data={"name": f"Товар {i}", "price": f"{100 + i}.00"},
        )
        assert resp.status_code == 200
        product_ids.append(resp.json()["data"]["id"])

    # Создаём теги
    tag_ids = []
    for name in ["тег_a", "тег_b"]:
        tag_resp = await authorized_client.post(
            "/product/tags",
            json={"name": name},
        )
        tag_ids.append(tag_resp.json()["data"]["tag_id"])

    # Привязываем: товар 0 -> тег 0, товар 1 -> тег 1
    await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_ids[0], "tag_id": tag_ids[0]},
    )
    await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_ids[1], "tag_id": tag_ids[1]},
    )

    # Получаем список
    response = await authorized_client.get("/product")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    result = ProductListResponse(**body["data"])
    assert result.total >= 2

    # Находим наши товары
    for item in result.items:
        if item.id == product_ids[0]:
            assert len(item.tags) == 1
            assert item.tags[0].name == "тег_a"
        elif item.id == product_ids[1]:
            assert len(item.tags) == 1
            assert item.tags[0].name == "тег_b"


# ============================================================
# SEARCH PRODUCTS WITH TAGS
# ============================================================


@pytest.mark.asyncio
async def test_search_products_200_includes_tags(authorized_client):
    """Поиск товаров включает теги."""
    # Создаём товар
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "УникальныйПоисковыйТовар", "price": "500.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    # Создаём тег и привязываем
    tag_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "поисковый", "description": "Для поиска"},
    )
    tag_id = tag_resp.json()["data"]["tag_id"]

    await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": tag_id},
    )

    # Ищем
    response = await authorized_client.get(
        "/product/search",
        params={"query": "УникальныйПоисковыйТовар"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    assert body["data"]["total"] >= 1
    items = body["data"]["items"]

    # Находим наш товар
    found = None
    for item in items:
        if item["id"] == product_id:
            found = item
            break

    assert found is not None
    assert len(found["tags"]) == 1
    assert found["tags"][0]["name"] == "поисковый"
    assert found["tags"][0]["description"] == "Для поиска"


# ============================================================
# FILTER PRODUCTS WITH TAGS
# ============================================================


@pytest.mark.asyncio
async def test_filter_products_200_includes_tags(authorized_client):
    """Фильтрация товаров включает теги."""
    # Создаём товар
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "ФильтрТовар", "price": "777.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    # Создаём тег и привязываем
    tag_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "фильтр", "description": "Для фильтрации"},
    )
    tag_id = tag_resp.json()["data"]["tag_id"]

    await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": tag_id},
    )

    # Фильтруем по имени
    response = await authorized_client.get(
        "/product",
        params={"name": "ФильтрТовар"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    items = body["data"]["items"]
    assert len(items) >= 1

    # Находим наш товар
    found = None
    for item in items:
        if item["id"] == product_id:
            found = item
            break

    assert found is not None
    assert len(found["tags"]) == 1
    assert found["tags"][0]["name"] == "фильтр"
