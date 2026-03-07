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

    # Получаем страницу
    response = await client.get("/cms/about")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    page = PageReadSchema(**body["data"])
    assert page.slug == "about"
    assert page.title == "О компании"
    assert page.is_published is True


@pytest.mark.asyncio
async def test_get_page_404_not_found(client):
    """Тест получения несуществующей страницы."""
    response = await client.get("/cms/non-existent-page")

    assert response.status_code == 404
    body = response.json()
    # Проверяем что ответ содержит ошибку
    assert "error" in body or body.get("success") is False


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
    response = await client.get("/cms/draft-page")

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

    # Получаем страницу
    response = await client.get("/cms/home")

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

    # Получаем страницу
    response = await client.get("/cms/sorted-page")

    assert response.status_code == 200
    body = response.json()
    page = PageReadSchema(**body["data"])

    # Блоки должны быть отсортированы по order
    assert [b.order for b in page.blocks] == [0, 1, 2]
    assert page.blocks[0].block_type == "banner"
    assert page.blocks[1].block_type == "hero"
    assert page.blocks[2].block_type == "text"
