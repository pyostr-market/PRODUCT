import pytest

@pytest.mark.asyncio
async def test_create_page_200(authorized_client):
    response = await authorized_client.post(
        "/cms/pages",
        json={
            "slug": "about",
            "title": "О нас",
            "is_published": True
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert body["data"]["slug"] == "about"
    assert body["data"]["title"] == "О нас"


@pytest.mark.asyncio
async def test_update_page_200(authorized_client):
    create = await authorized_client.post(
        "/cms/pages",
        json={
            "slug": "contacts",
            "title": "Контакты"
        },
    )

    page_id = create.json()["data"]["id"]

    response = await authorized_client.patch(
        f"/cms/pages/{page_id}",
        json={
            "title": "Контакты компании"
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Контакты компании"


@pytest.mark.asyncio
async def test_delete_page_200(authorized_client):
    create = await authorized_client.post(
        "/cms/pages",
        json={
            "slug": "privacy",
            "title": "Privacy Policy"
        },
    )

    page_id = create.json()["data"]["id"]

    response = await authorized_client.delete(
        f"/cms/pages/{page_id}"
    )

    assert response.status_code == 200
    assert response.json()["success"] is True