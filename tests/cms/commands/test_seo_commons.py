import pytest


@pytest.mark.asyncio
async def test_create_seo_200(authorized_client):

    response = await authorized_client.post(
        "/cms/seo",
        json={
            "page_slug": "home",
            "title": "Marketplace",
            "description": "Best marketplace"
        }
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_seo_200(authorized_client):

    create = await authorized_client.post(
        "/cms/seo",
        json={
            "page_slug": "about",
            "title": "About"
        }
    )

    seo_id = create.json()["data"]["id"]

    response = await authorized_client.patch(
        f"/cms/seo/{seo_id}",
        json={
            "title": "About company"
        }
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_seo_200(authorized_client):

    create = await authorized_client.post(
        "/cms/seo",
        json={
            "page_slug": "contacts"
        }
    )

    seo_id = create.json()["data"]["id"]

    response = await authorized_client.delete(
        f"/cms/seo/{seo_id}"
    )

    assert response.status_code == 200