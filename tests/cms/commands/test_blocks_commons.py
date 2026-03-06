import pytest

@pytest.mark.asyncio
async def test_create_block_200(authorized_client):

    page = await authorized_client.post(
        "/cms/pages",
        json={"slug": "home", "title": "Главная"}
    )

    page_id = page.json()["data"]["id"]

    response = await authorized_client.post(
        "/cms/blocks",
        json={
            "page_id": page_id,
            "type": "carousel",
            "order": 0,
            "data": {
                "slides": []
            }
        }
    )

    assert response.status_code == 200
    assert response.json()["data"]["type"] == "carousel"


@pytest.mark.asyncio
async def test_update_block_200(authorized_client):

    page = await authorized_client.post(
        "/cms/pages",
        json={"slug": "home2", "title": "Главная"}
    )

    page_id = page.json()["data"]["id"]

    block = await authorized_client.post(
        "/cms/blocks",
        json={
            "page_id": page_id,
            "type": "text",
            "order": 1,
            "data": {"text": "old"}
        }
    )

    block_id = block.json()["data"]["id"]

    response = await authorized_client.patch(
        f"/cms/blocks/{block_id}",
        json={"data": {"text": "new"}}
    )

    assert response.status_code == 200
    assert response.json()["data"]["data"]["text"] == "new"


@pytest.mark.asyncio
async def test_delete_block_200(authorized_client):

    page = await authorized_client.post(
        "/cms/pages",
        json={"slug": "home3", "title": "Главная"}
    )

    page_id = page.json()["data"]["id"]

    block = await authorized_client.post(
        "/cms/blocks",
        json={
            "page_id": page_id,
            "type": "banner",
            "order": 1,
            "data": {}
        }
    )

    block_id = block.json()["data"]["id"]

    response = await authorized_client.delete(
        f"/cms/blocks/{block_id}"
    )

    assert response.status_code == 200