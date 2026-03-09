"""Тесты для получения страниц (Page Queries)."""

import pytest

from src.cms.api.schemas.page_schemas import PageReadSchema


@pytest.mark.asyncio
async def test_get_page_200(authorized_client, client):
    """Тест успешного получения опубликованной страницы."""
    # Создаём страницу
    await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "about",
            "title": "О компании",
            "is_published": True,
        },
    )

    # Получаем страницу по slug
    response = await client.get("/cms/pages/slug/about")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    page = PageReadSchema(**body["data"])
    assert page.slug == "about"
    assert page.title == "О компании"
    assert page.is_published is True


@pytest.mark.asyncio
async def test_get_page_by_id_200(authorized_client, client):
    """Тест успешного получения страницы по ID."""
    # Создаём страницу
    create_response = await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "about-id",
            "title": "О компании ID",
            "is_published": True,
        },
    )
    page_id = create_response.json()["data"]["id"]

    # Получаем страницу по ID
    response = await client.get(f"/cms/pages/{page_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    page = PageReadSchema(**body["data"])
    assert page.id == page_id
    assert page.slug == "about-id"
    assert page.title == "О компании ID"


@pytest.mark.asyncio
async def test_get_page_404_not_found(client):
    """Тест получения несуществующей страницы."""
    response = await client.get("/cms/pages/slug/non-existent-page")

    assert response.status_code == 404
    body = response.json()
    # Проверяем что ответ содержит ошибку
    assert "error" in body or body.get("success") is False


@pytest.mark.asyncio
async def test_get_page_by_id_404_not_found(client):
    """Тест получения несуществующей страницы по ID."""
    response = await client.get("/cms/pages/999999")

    assert response.status_code == 404
    body = response.json()
    assert body.get("success") is False


@pytest.mark.asyncio
async def test_get_page_404_unpublished(client, authorized_client):
    """Тест получения неопубликованной страницы (должна возвращать 404)."""
    # Создаём неопубликованную страницу
    await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "draft-page",
            "title": "Черновик",
            "is_published": False,
        },
    )

    # Пытаемся получить страницу (должна вернуть 404)
    response = await client.get("/cms/pages/slug/draft-page")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_page_with_blocks(authorized_client, client):
    """Тест получения страницы с блоками."""
    # Создаём страницу с блоками
    await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "home",
            "title": "Главная",
            "is_published": True,
            "blocks": [
                {
                    "block_type": "hero",
                    "data": {"title": "Welcome", "subtitle": "To our store"},
                    "order": 0,
                },
                {
                    "block_type": "text",
                    "data": {"content": "<p>About us</p>"},
                    "order": 1,
                },
            ],
        },
    )

    # Получаем страницу по slug
    response = await client.get("/cms/pages/slug/home")

    assert response.status_code == 200
    body = response.json()
    page = PageReadSchema(**body["data"])

    assert len(page.blocks) == 2
    assert page.blocks[0].block_type == "hero"
    assert page.blocks[0].data["title"] == "Welcome"
    assert page.blocks[1].block_type == "text"


@pytest.mark.asyncio
async def test_get_page_blocks_sorted_by_order(authorized_client, client):
    """Тест сортировки блоков по порядку."""
    # Создаём страницу с блоками в неправильном порядке
    await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "sorted-page",
            "title": "Sorted Page",
            "is_published": True,
            "blocks": [
                {"block_type": "text", "data": {}, "order": 2},
                {"block_type": "banner", "data": {}, "order": 0},
                {"block_type": "hero", "data": {}, "order": 1},
            ],
        },
    )

    # Получаем страницу по slug
    response = await client.get("/cms/pages/slug/sorted-page")

    assert response.status_code == 200
    body = response.json()
    page = PageReadSchema(**body["data"])

    # Блоки должны быть отсортированы по order
    assert [b.order for b in page.blocks] == [0, 1, 2]
    assert page.blocks[0].block_type == "banner"
    assert page.blocks[1].block_type == "hero"
    assert page.blocks[2].block_type == "text"


@pytest.mark.asyncio
async def test_search_pages_200(authorized_client, client):
    """Тест поиска страниц по заголовку."""
    # Создаём страницы
    await authorized_client.post(
        "/cms/admin",
        json={"slug": "about-us", "title": "О компании", "is_published": True},
    )
    await authorized_client.post(
        "/cms/admin",
        json={"slug": "contact", "title": "Контакты", "is_published": True},
    )

    # Поиск по частичному совпадению
    response = await client.get("/cms/pages/search?q=компании")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] >= 1
    assert "О компании" in body["data"]["items"][0]["title"]

    # Поиск с пустым запросом (должны вернуться все страницы)
    response = await client.get("/cms/pages/search")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] >= 2


@pytest.mark.asyncio
async def test_search_pages_with_pagination(authorized_client, client):
    """Тест поиска страниц с пагинацией."""
    # Создаём страницы
    for i in range(15):
        await authorized_client.post(
            "/cms/admin",
            json={"slug": f"page-{i}", "title": f"Страница {i}", "is_published": True},
        )

    # Поиск с пагинацией
    response = await client.get("/cms/pages/search?q=Страница&limit=5&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 15
    assert len(body["data"]["items"]) == 5


@pytest.mark.asyncio
async def test_get_all_pages_with_filter(authorized_client, client):
    """Тест получения списка страниц с фильтрацией."""
    # Создаём страницы
    await authorized_client.post(
        "/cms/admin",
        json={"slug": "published", "title": "Опубликована", "is_published": True},
    )
    await authorized_client.post(
        "/cms/admin",
        json={"slug": "draft", "title": "Черновик", "is_published": False},
    )

    # Фильтр по статусу
    response = await client.get("/cms/pages?is_published=true&limit=10&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert body["data"]["items"][0]["title"] == "Опубликована"
