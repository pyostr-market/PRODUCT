"""Тесты для создания страниц (Page)."""

import pytest

from src.cms.api.schemas.page_schemas import PageReadSchema


@pytest.mark.asyncio
async def test_create_page_200(authorized_client):
    """Тест успешного создания страницы."""
    response = await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "about-us",
            "title": "О нас",
            "is_published": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    page = PageReadSchema(**body["data"])
    assert page.slug == "about-us"
    assert page.title == "О нас"
    assert page.is_published is True
    assert isinstance(page.id, int)


@pytest.mark.asyncio
async def test_create_page_with_blocks_200(authorized_client):
    """Тест создания страницы с блоками."""
    response = await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "home-page",
            "title": "Главная страница",
            "is_published": True,
            "blocks": [
                {
                    "block_type": "hero",
                    "data": {
                        "title": "Big Sale",
                        "subtitle": "Up to 50%",
                    },
                    "order": 0,
                },
                {
                    "block_type": "text",
                    "data": {
                        "content": "<p>Welcome to our store</p>",
                    },
                    "order": 1,
                },
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    page = PageReadSchema(**body["data"])
    assert page.slug == "home-page"
    assert len(page.blocks) == 2
    assert page.blocks[0].block_type == "hero"
    assert page.blocks[1].block_type == "text"


@pytest.mark.asyncio
async def test_create_page_400_slug_too_short(authorized_client):
    """Тест создания страницы с коротким slug."""
    response = await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "a",
            "title": "Тест",
        },
    )

    # Pydantic валидация возвращает 422
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_page_400_invalid_slug_format(authorized_client):
    """Тест создания страницы с некорректным форматом slug."""
    response = await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "invalid_slug_with_caps",
            "title": "Тест",
        },
    )

    # Pydantic валидация возвращает 422
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_page_400_slug_already_exists(authorized_client):
    """Тест создания страницы с существующим slug."""
    # Создаём первую страницу
    await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "duplicate-page",
            "title": "Первая страница",
        },
    )

    # Пытаемся создать вторую с таким же slug
    response = await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "duplicate-page",
            "title": "Вторая страница",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "slug" in body["error"]["message"].lower()


@pytest.mark.asyncio
async def test_create_page_400_title_too_short(authorized_client):
    """Тест создания страницы с коротким заголовком."""
    response = await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "test-page",
            "title": "A",
        },
    )

    # Pydantic валидация возвращает 422
    assert response.status_code == 422
