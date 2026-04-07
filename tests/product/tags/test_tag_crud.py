import json

import pytest

from src.catalog.product.api.schemas.schemas import (
    TagReadSchema,
    TagListResponse,
    ProductTagReadSchema,
    ProductTagListResponse,
    ProductReadSchema,
)


# ============================================================
# CREATE TAG
# ============================================================


@pytest.mark.asyncio
async def test_create_tag_200(authorized_client):
    """Создание тега успешно."""
    response = await authorized_client.post(
        "/product/tags",
        json={
            "name": "популярный",
            "description": "Популярные товары",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    tag = TagReadSchema(**body["data"])
    assert isinstance(tag.tag_id, int)
    assert tag.name == "популярный"
    assert tag.description == "Популярные товары"


@pytest.mark.asyncio
async def test_create_tag_200_no_description(authorized_client):
    """Создание тега без описания."""
    response = await authorized_client.post(
        "/product/tags",
        json={"name": "новинка"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    tag = TagReadSchema(**body["data"])
    assert tag.name == "новинка"
    assert tag.description is None


@pytest.mark.asyncio
async def test_create_tag_409_duplicate_name(authorized_client):
    """Ошибка при создании тега с дублирующимся именем."""
    # Создаём первый тег
    resp1 = await authorized_client.post(
        "/product/tags",
        json={"name": "хит", "description": "Хит продаж"},
    )
    assert resp1.status_code == 200

    # Пытаемся создать такой же
    response = await authorized_client.post(
        "/product/tags",
        json={"name": "хит", "description": "Другое описание"},
    )

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_create_tag_422_name_too_long(authorized_client):
    """Ошибка валидации: имя тега слишком длинное."""
    response = await authorized_client.post(
        "/product/tags",
        json={"name": "a" * 101},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tag_422_description_too_long(authorized_client):
    """Ошибка валидации: описание тега слишком длинное."""
    response = await authorized_client.post(
        "/product/tags",
        json={
            "name": "тест",
            "description": "b" * 501,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_tag_422_missing_name(authorized_client):
    """Ошибка валидации: отсутствие имени тега."""
    response = await authorized_client.post(
        "/product/tags",
        json={"description": "Без имени"},
    )

    assert response.status_code == 422


# ============================================================
# GET TAG BY ID
# ============================================================


@pytest.mark.asyncio
async def test_get_tag_by_id_200(authorized_client, test_tags):
    """Получение тега по ID."""
    tag_id = test_tags[0]["tag_id"]

    response = await authorized_client.get(f"/product/tags/{tag_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    tag = TagReadSchema(**body["data"])
    assert tag.tag_id == tag_id
    assert tag.name == test_tags[0]["name"]
    assert tag.description == test_tags[0]["description"]


@pytest.mark.asyncio
async def test_get_tag_by_id_404(authorized_client):
    """Получение несуществующего тега."""
    response = await authorized_client.get("/product/tags/999999")

    assert response.status_code == 404
    body = response.json()
    assert "detail" in body


# ============================================================
# GET ALL TAGS
# ============================================================


@pytest.mark.asyncio
async def test_get_all_tags_200(authorized_client, test_tags):
    """Получение списка всех тегов."""
    response = await authorized_client.get("/product/tags")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    result = TagListResponse(**body["data"])
    assert result.total >= 3
    assert len(result.items) >= 3

    # Проверя, что наши теги на месте
    names = {item.name for item in result.items}
    assert "популярный" in names
    assert "новинка" in names
    assert "распродажа" in names


@pytest.mark.asyncio
async def test_get_all_tags_pagination(authorized_client):
    """Пагинация при получении тегов."""
    # Создаём 5 тегов
    for i in range(5):
        await authorized_client.post(
            "/product/tags",
            json={"name": f"tag_{i}", "description": f"Tag {i}"},
        )

    # Получаем первые 2
    response = await authorized_client.get("/product/tags", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    body = response.json()
    result = TagListResponse(**body["data"])
    assert len(result.items) == 2
    assert result.total == 5

    # Получаем оставшиеся 3
    response = await authorized_client.get("/product/tags", params={"limit": 10, "offset": 2})
    assert response.status_code == 200
    body = response.json()
    result = TagListResponse(**body["data"])
    assert len(result.items) == 3


@pytest.mark.asyncio
async def test_get_all_tags_200_empty(client):
    """Получение пустого списка тегов."""
    response = await client.get("/product/tags")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    result = TagListResponse(**body["data"])
    assert result.total == 0
    assert len(result.items) == 0


# ============================================================
# UPDATE TAG
# ============================================================


@pytest.mark.asyncio
async def test_update_tag_200(authorized_client, test_tags):
    """Обновление тега успешно."""
    tag_id = test_tags[0]["tag_id"]

    response = await authorized_client.put(
        f"/product/tags/{tag_id}",
        json={
            "name": "хит продаж",
            "description": "Самые продаваемые товары",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    tag = TagReadSchema(**body["data"])
    assert tag.tag_id == tag_id
    assert tag.name == "хит продаж"
    assert tag.description == "Самые продаваемые товары"


@pytest.mark.asyncio
async def test_update_tag_200_partial(authorized_client, test_tags):
    """Частичное обновление тега."""
    tag_id = test_tags[2]["tag_id"]  # "распродажа" без description

    response = await authorized_client.put(
        f"/product/tags/{tag_id}",
        json={"description": "Скидки до 50%"},
    )

    assert response.status_code == 200
    body = response.json()
    tag = TagReadSchema(**body["data"])
    assert tag.name == "распродажа"  # имя не изменилось
    assert tag.description == "Скидки до 50%"


@pytest.mark.asyncio
async def test_update_tag_404(authorized_client):
    """Обновление несуществующего тега."""
    response = await authorized_client.put(
        "/product/tags/999999",
        json={"name": "новый"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_tag_409_duplicate_name(authorized_client, test_tags):
    """Обновление с дублирующимся именем."""
    # test_tags[0] = "популярный", test_tags[1] = "новинка"
    # Пытаемся переименовать "популярный" в "новинка"
    response = await authorized_client.put(
        f"/product/tags/{test_tags[0]['tag_id']}",
        json={"name": "новинка"},
    )

    assert response.status_code == 409
    body = response.json()
    assert body["success"] is False


# ============================================================
# DELETE TAG
# ============================================================


@pytest.mark.asyncio
async def test_delete_tag_200(authorized_client):
    """Удаление тега."""
    # Создаём тег для удаления
    create_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "удаляемый", "description": "Временный тег"},
    )
    tag_id = create_resp.json()["data"]["tag_id"]

    # Удаляем
    response = await authorized_client.delete(f"/product/tags/{tag_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Тег удален"

    # Проверяем, что тег больше не существует
    get_resp = await authorized_client.get(f"/product/tags/{tag_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_tag_cascades_to_product_tags(authorized_client):
    """При удалении тега связи product_tags удаляются каскадно."""
    # Создаём товар
    product_resp = await authorized_client.post(
        "/product",
        data={"name": "Товар для каскада", "price": "100.00"},
    )
    product_id = product_resp.json()["data"]["id"]

    # Создаём тег
    tag_resp = await authorized_client.post(
        "/product/tags",
        json={"name": "каскадный", "description": "Для теста каскада"},
    )
    tag_id = tag_resp.json()["data"]["tag_id"]

    # Привязываем тег к товару
    link_resp = await authorized_client.post(
        "/product/tags/product-tags",
        json={"product_id": product_id, "tag_id": tag_id},
    )
    assert link_resp.status_code == 200

    # Удаляем тег
    delete_resp = await authorized_client.delete(f"/product/tags/{tag_id}")
    assert delete_resp.status_code == 200

    # Проверяем, что у товара больше нет тегов
    get_tags_resp = await authorized_client.get(f"/product/tags/product-tags/{product_id}")
    assert get_tags_resp.status_code == 200
    body = get_tags_resp.json()
    assert body["data"]["total"] == 0
