"""Тесты для SEO (Commands и Queries)."""

import pytest

from src.cms.api.schemas.seo_schemas import SeoReadSchema


@pytest.mark.asyncio
async def test_create_seo_200(authorized_client):
    """Тест успешного создания SEO данных."""
    response = await authorized_client.post(
        "/cms/seo/admin",
        json={
            "page_slug": "about-us",
            "title": "О нас - Компания",
            "description": "Узнайте больше о нашей компании",
            "keywords": ["компания", "о нас", "информация"],
            "og_image_id": 123,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    seo = SeoReadSchema(**body["data"])
    assert seo.page_slug == "about-us"
    assert seo.title == "О нас - Компания"
    assert seo.description == "Узнайте больше о нашей компании"
    assert seo.keywords == ["компания", "о нас", "информация"]
    assert seo.og_image_id == 123


@pytest.mark.asyncio
async def test_create_seo_200_minimal(authorized_client):
    """Тест создания SEO с минимальными данными."""
    response = await authorized_client.post(
        "/cms/seo/admin",
        json={
            "page_slug": "minimal-page",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    seo = SeoReadSchema(**body["data"])
    assert seo.page_slug == "minimal-page"
    assert seo.title is None
    assert seo.description is None
    assert seo.keywords == []


@pytest.mark.asyncio
async def test_update_seo_200(authorized_client):
    """Тест успешного обновления SEO данных."""
    # Создаём SEO
    create_response = await authorized_client.post(
        "/cms/seo/admin",
        json={
            "page_slug": "update-page",
            "title": "Old Title",
            "description": "Old Description",
        },
    )
    assert create_response.status_code == 200
    seo_id = create_response.json()["data"]["id"]

    # Обновляем SEO
    update_response = await authorized_client.put(
        f"/cms/seo/admin/{seo_id}",
        json={
            "title": "New Title",
            "description": "New Description",
            "keywords": ["new", "keywords"],
            "og_image_id": 456,
        },
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["success"] is True

    seo = SeoReadSchema(**body["data"])
    assert seo.title == "New Title"
    assert seo.description == "New Description"
    assert seo.keywords == ["new", "keywords"]
    assert seo.og_image_id == 456


@pytest.mark.asyncio
async def test_update_seo_404_not_found(authorized_client):
    """Тест обновления несуществующих SEO данных."""
    response = await authorized_client.put(
        "/cms/seo/admin/999999",
        json={"title": "New"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_delete_seo_200(authorized_client):
    """Тест успешного удаления SEO данных."""
    # Создаём SEO
    create_response = await authorized_client.post(
        "/cms/seo/admin",
        json={"page_slug": "to-delete", "title": "ToDelete"},
    )
    assert create_response.status_code == 200
    seo_id = create_response.json()["data"]["id"]

    # Удаляем SEO
    delete_response = await authorized_client.delete(
        f"/cms/seo/admin/{seo_id}"
    )

    assert delete_response.status_code == 200
    body = delete_response.json()
    assert body["success"] is True
    assert body["data"]["seo_id"] == seo_id


@pytest.mark.asyncio
async def test_delete_seo_404_not_found(authorized_client):
    """Тест удаления несуществующих SEO данных."""
    response = await authorized_client.delete("/cms/seo/admin/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_get_seo_meta_200(authorized_client, client):
    """Тест получения SEO meta данных для страницы."""
    # Создаём SEO
    await authorized_client.post(
        "/cms/seo/admin",
        json={
            "page_slug": "meta-page",
            "title": "Meta Title",
            "description": "Meta Description",
            "keywords": ["meta", "tags"],
            "og_image_id": 789,
        },
    )

    # Получаем meta
    response = await client.get("/cms/seo/meta-page/meta")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == "Meta Title"
    assert body["data"]["description"] == "Meta Description"
    assert body["data"]["keywords"] == "meta, tags"
    assert body["data"]["og_image_id"] == 789


@pytest.mark.asyncio
async def test_get_seo_meta_404_not_found(client):
    """Тест получения несуществующих SEO meta данных."""
    response = await client.get("/cms/seo/non-existent/meta")

    assert response.status_code == 404
    body = response.json()
    # Проверяем что ответ содержит ошибку
    assert "error" in body or body.get("success") is False


@pytest.mark.asyncio
async def test_create_seo_with_page_relation(authorized_client, client):
    """Тест создания SEO для существующей страницы."""
    # Создаём страницу
    page_response = await authorized_client.post(
        "/cms/admin",
        json={"slug": "related-page", "title": "Related Page"},
    )
    assert page_response.status_code == 200

    # Создаём SEO для этой страницы
    seo_response = await authorized_client.post(
        "/cms/seo/admin",
        json={
            "page_slug": "related-page",
            "title": "SEO for Related Page",
        },
    )

    assert seo_response.status_code == 200

    # Проверяем получение meta
    meta_response = await client.get("/cms/seo/related-page/meta")
    assert meta_response.status_code == 200
    assert meta_response.json()["data"]["title"] == "SEO for Related Page"
