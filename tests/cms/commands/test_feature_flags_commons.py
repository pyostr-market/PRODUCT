import pytest


@pytest.mark.asyncio
async def test_create_feature_flag_200(authorized_client):

    response = await authorized_client.post(
        "/cms/feature-flags",
        json={
            "key": "chat_enabled",
            "enabled": True
        }
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_feature_flag_200(authorized_client):

    create = await authorized_client.post(
        "/cms/feature-flags",
        json={
            "key": "login_enabled",
            "enabled": True
        }
    )

    flag_id = create.json()["data"]["id"]

    response = await authorized_client.patch(
        f"/cms/feature-flags/{flag_id}",
        json={"enabled": False}
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_feature_flag_200(authorized_client):

    create = await authorized_client.post(
        "/cms/feature-flags",
        json={
            "key": "delete_flag"
        }
    )

    flag_id = create.json()["data"]["id"]

    response = await authorized_client.delete(
        f"/cms/feature-flags/{flag_id}"
    )

    assert response.status_code == 200