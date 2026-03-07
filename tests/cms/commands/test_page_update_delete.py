"""Тесты для обновления и удаления страниц (Page)."""

import pytest

from src.cms.api.schemas.page_schemas import PageReadSchema


@pytest.mark.asyncio
async def test_update_page_200(authorized_client):
    """Тест успешного обновления страницы."""
    # Создаём страницу
    create_response = await authorized_client.post(
        "/cms/admin",
        json={
            "slug": "old-slug",
            "title": "Old Title",
            "is_published": False,
        },
    )
    assert create_response.status_code == 200
    page_id = create_response.json()["data"]["id"]

    # Обновляем страницу
    update_response = await authorized_client.put(
        f"/cms/admin/{page_id}",
        json={
            "slug": "new-slug",
            "title": "New Title",
            "is_published": True,
        },
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["success"] is True

    page = PageReadSchema(**body["data"])
    assert page.slug == "new-slug"
    assert page.title == "New Title"
    assert page.is_published is True


@pytest.mark.asyncio
async def test_update_page_404_not_found(authorized_client):
    """Тест обновления несуществующей страницы."""
    response = await authorized_client.put(
        "/cms/admin/999999",
        json={
            "title": "New Title",
        },
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_update_page_400_slug_already_exists(authorized_client):
    """Тест обновления страницы с существующим slug."""
    # Создаём две страницы
    await authorized_client.post(
        "/cms/admin",
        json={"slug": "page-one", "title": "Page One"},
    )
    create_response = await authorized_client.post(
        "/cms/admin",
        json={"slug": "page-two", "title": "Page Two"},
    )
    page_two_id = create_response.json()["data"]["id"]

    # Пытаемся изменить slug второй страницы на slug первой
    response = await authorized_client.put(
        f"/cms/admin/{page_two_id}",
        json={"slug": "page-one"},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert "slug" in body["error"]["message"].lower()


@pytest.mark.asyncio
async def test_delete_page_200(authorized_client):
    """Тест успешного удаления страницы."""
    # Создаём страницу
    create_response = await authorized_client.post(
        "/cms/admin",
        json={"slug": "to-delete", "title": "ToDelete"},
    )
    assert create_response.status_code == 200
    page_id = create_response.json()["data"]["id"]

    # Удаляем страницу
    delete_response = await authorized_client.delete(f"/cms/admin/{page_id}")

    assert delete_response.status_code == 200
    body = delete_response.json()
    assert body["success"] is True
    assert body["data"]["page_id"] == page_id

    # Проверяем, что страница удалена
    get_response = await authorized_client.get("/cms/to-delete")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_page_404_not_found(authorized_client):
    """Тест удаления несуществующей страницы."""
    response = await authorized_client.delete("/cms/admin/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_add_page_block_200(authorized_client):
    """Тест добавления блока на страницу."""
    # Создаём страницу
    create_response = await authorized_client.post(
        "/cms/admin",
        json={"slug": "page-with-blocks", "title": "Page With Blocks"},
    )
    assert create_response.status_code == 200
    page_id = create_response.json()["data"]["id"]

    # Добавляем блок
    add_block_response = await authorized_client.post(
        f"/cms/admin/{page_id}/blocks",
        json={
            "block_type": "banner",
            "data": {"title": "Banner Title", "image_url": "/img/banner.jpg"},
        },
    )

    assert add_block_response.status_code == 200
    body = add_block_response.json()
    assert body["success"] is True
    assert "block_id" in body["data"]

    # Проверяем, что блок добавился
    get_response = await authorized_client.get("/cms/page-with-blocks")
    assert get_response.status_code == 200
    page_data = get_response.json()["data"]
    assert len(page_data["blocks"]) == 1
    assert page_data["blocks"][0]["block_type"] == "banner"


@pytest.mark.asyncio
async def test_add_page_block_404_page_not_found(authorized_client):
    """Тест добавления блока на несуществующую страницу."""
    response = await authorized_client.post(
        "/cms/admin/999999/blocks",
        json={"block_type": "text", "data": {}},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
