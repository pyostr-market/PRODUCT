import pytest

@pytest.mark.asyncio
async def test_get_pages_list_200(authorized_client):
    response = await authorized_client.get("/cms/pages")

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert isinstance(body["data"], list)


@pytest.mark.asyncio
async def test_get_page_by_id_200(authorized_client):
    create = await authorized_client.post(
        "/cms/pages",
        json={
            "slug": "assets",
            "title": "Assets"
        },
    )

    page_id = create.json()["data"]["id"]

    response = await authorized_client.get(
        f"/cms/pages/{page_id}"
    )

    assert response.status_code == 200
    assert response.json()["data"]["id"] == page_id


@pytest.mark.asyncio
async def test_get_page_by_slug_200(authorized_client):
    await authorized_client.post(
        "/cms/pages",
        json={
            "slug": "faq",
            "title": "FAQ"
        },
    )

    response = await authorized_client.get(
        "/cms/pages/slug/faq"
    )

    assert response.status_code == 200
    assert response.json()["data"]["slug"] == "faq"