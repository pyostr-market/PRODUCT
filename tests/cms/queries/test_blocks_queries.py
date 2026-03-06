import pytest

@pytest.mark.asyncio
async def test_get_blocks_by_page_200(authorized_client):

    page = await authorized_client.post(
        "/cms/pages",
        json={"slug": "home4", "title": "Главная"}
    )

    page_id = page.json()["data"]["id"]

    await authorized_client.post(
        "/cms/blocks",
        json={
            "page_id": page_id,
            "type": "text",
            "order": 0,
            "data": {"text": "hello"}
        }
    )

    response = await authorized_client.get(
        f"/cms/pages/{page_id}/blocks"
    )

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)