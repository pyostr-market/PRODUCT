import json

import pytest

from src.catalog.product.api.schemas.schemas import (
    ProductTagReadSchema,
    ProductTagListResponse,
    TagReadSchema,
    ProductReadSchema,
)


# ============================================================
# ADD TAG TO PRODUCT
# ============================================================


@pytest.mark.asyncio
async def test_add_tag_to_product_200(authorized_client):
    """Успешная привязка тега к товару."""
    # Создаём товар
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Тестовый товар", "price": "500.00"},
    )
    assert product_resp.status_code == 200
    product_id = product_resp.json()["data"]["id"]

    # Создаём тег
    tag_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "эксклюзив", "description": "Эксклюзивные товары"},
    )
    assert tag_resp.status_code == 200
    tag_id = tag_resp.json()["data"]["tag_id"]

    # Привязываем тег к товару
    response = await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": tag_id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    link = ProductTagReadSchema(**body["data"])
    assert link.product_id == product_id
    assert link.tag_id == tag_id
    assert link.tag.tag_id == tag_id
    assert link.tag.name == "эксклюзив"
    assert link.tag.description == "Эксклюзивные товары"


@pytest.mark.asyncio
async def test_add_tag_to_product_400_duplicate(authorized_client):
    """Ошибка при повторной привязке того же тега."""
    # Создаём товар
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Дублирующий товар", "price": "100.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    # Создаём тег
    tag_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "дубль"},
    )
    tag_id = tag_resp.json()["data"]["tag_id"]

    # Первая привязка — успешно
    resp1 = await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": tag_id},
    )
    assert resp1.status_code == 200

    # Вторая привязка — ошибка
    response = await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": tag_id},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_add_tag_to_product_404_product_not_found(authorized_client):
    """Привязка тега к несуществующему товару."""
    tag_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "сирота"},
    )
    tag_id = tag_resp.json()["data"]["tag_id"]

    response = await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": 999999, "tag_id": tag_id},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_tag_to_product_404_tag_not_found(authorized_client):
    """Привязка несуществующего тега к товару."""
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Без тега", "price": "200.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    response = await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": 999999},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_add_multiple_tags_to_product(authorized_client):
    """Привязка нескольких тегов к одному товару."""
    # Создаём товар
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Мульти-тег товар", "price": "300.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    # Создаём 3 тега
    tag_ids = []
    for name in ["популярный", "новый", "качественный"]:
        tag_resp = await authorized_client.post(
            "/product/tags",
            json={"name": name, "description": f"Тег: {name}"},
        )
        tag_ids.append(tag_resp.json()["data"]["tag_id"])

    # Привязываем все теги
    for tag_id in tag_ids:
        resp = await authorized_client.post(
            "/product/tags/product-tags",
            json={"product_id": product_id, "tag_id": tag_id},
        )
        assert resp.status_code == 200

    # Проверяем, что все теги привязаны
    get_resp = await authorized_client.get(f"/product/tags/product-tags/{product_id}")
    assert get_resp.status_code == 200
    body = get_resp.json()
    result = ProductTagListResponse(**body["data"])
    assert result.total == 3


# ============================================================
# REMOVE TAG FROM PRODUCT
# ============================================================


@pytest.mark.asyncio
async def test_remove_tag_from_product_200(authorized_client):
    """Удаление тега у товара."""
    # Создаём товар
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Товар для удаления тега", "price": "400.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    # Создаём тег
    tag_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "временный"},
    )
    tag_id = tag_resp.json()["data"]["tag_id"]

    # Привязываем
    link_resp = await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": tag_id},
    )
    assert link_resp.status_code == 200

    # Удаляем связь
    response = await authorized_client.delete(
        f"/product/tags/product-tags/{product_id}/{tag_id}"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Тег удален из товара"

    # Проверяем, что тег больше не привязан
    get_resp = await authorized_client.get(f"/product/tags/product-tags/{product_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()["data"]
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_remove_tag_from_product_404_not_found(authorized_client):
    """Удаление несуществующей связи."""
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Без связи", "price": "50.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    tag_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "непривязанный"},
    )
    tag_id = tag_resp.json()["data"]["tag_id"]

    response = await authorized_client.delete(
        f"/product/tags/product-tags/{product_id}/{tag_id}"
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_remove_tag_from_product_404_wrong_tag(authorized_client):
    """Удаление связи с неправильным tag_id."""
    # Создаём товар и тег
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Товар", "price": "75.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    tag1_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "тег1"},
    )
    tag1_id = tag1_resp.json()["data"]["tag_id"]

    tag2_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "тег2"},
    )
    tag2_id = tag2_resp.json()["data"]["tag_id"]

    # Привязываем тег1
    await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": tag1_id},
    )

    # Пытаемся удалить тег2 (который не привязан)
    response = await authorized_client.delete(
        f"/product/tags/product-tags/{product_id}/{tag2_id}"
    )

    assert response.status_code == 404


# ============================================================
# GET PRODUCT TAGS
# ============================================================


@pytest.mark.asyncio
async def test_get_product_tags_200(authorized_client, product_with_tags):
    """Получение всех тегов товара."""
    product_id = product_with_tags["product"]["id"]
    expected_tags = product_with_tags["tags"]

    response = await authorized_client.get(f"/product/tags/product-tags/{product_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    result = ProductTagListResponse(**body["data"])
    assert result.total == 2
    assert len(result.items) == 2

    # Проверяем, что все ожидаемые теги присутствуют
    tag_names = {item.tag.name for item in result.items}
    assert "популярный" in tag_names
    assert "новинка" in tag_names


@pytest.mark.asyncio
async def test_get_product_tags_empty(authorized_client):
    """Получение тегов товара без тегов."""
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Без тегов", "price": "999.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    response = await authorized_client.get(f"/product/tags/product-tags/{product_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    result = ProductTagListResponse(**body["data"])
    assert result.total == 0
    assert len(result.items) == 0


@pytest.mark.asyncio
async def test_get_product_tags_pagination(authorized_client):
    """Пагинация при получении тегов товара."""
    # Создаём товар
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Товар с пагинацией", "price": "100.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    # Создаём 5 тегов и привязываем
    for i in range(5):
        tag_resp = await authorized_client.post(
            "/product/tags",
            json={"name": f"page_tag_{i}"},
        )
        tag_id = tag_resp.json()["data"]["tag_id"]
        await authorized_client.post(
            "/product/tags/product-tags",
            json={"product_id": product_id, "tag_id": tag_id},
        )

    # Получаем первые 2
    resp = await authorized_client.get(
        f"/product/tags/product-tags/{product_id}",
        params={"limit": 2, "offset": 0},
    )
    assert resp.status_code == 200
    result = ProductTagListResponse(**resp.json()["data"])
    assert len(result.items) == 2
    assert result.total == 5

    # Получаем оставшиеся 3
    resp = await authorized_client.get(
        f"/product/tags/product-tags/{product_id}",
        params={"limit": 10, "offset": 2},
    )
    assert resp.status_code == 200
    result = ProductTagListResponse(**resp.json()["data"])
    assert len(result.items) == 3
