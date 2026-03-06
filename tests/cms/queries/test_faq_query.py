import pytest

@pytest.mark.asyncio
async def test_get_faq_list_200(authorized_client):

    response = await authorized_client.get("/cms/faq")

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)