import pytest


@pytest.mark.asyncio
async def test_create_email_template_200(authorized_client):

    response = await authorized_client.post(
        "/cms/email-templates",
        json={
            "key": "user_registered",
            "subject": "Welcome",
            "body_html": "<p>Hello {{name}}</p>"
        }
    )

    assert response.status_code == 200
    assert response.json()["data"]["key"] == "user_registered"


@pytest.mark.asyncio
async def test_update_email_template_200(authorized_client):

    create = await authorized_client.post(
        "/cms/email-templates",
        json={
            "key": "password_reset",
            "subject": "Reset",
            "body_html": "reset"
        }
    )

    template_id = create.json()["data"]["id"]

    response = await authorized_client.patch(
        f"/cms/email-templates/{template_id}",
        json={
            "subject": "Reset password"
        }
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_email_template_200(authorized_client):

    create = await authorized_client.post(
        "/cms/email-templates",
        json={
            "key": "delete_test",
            "subject": "Test"
        }
    )

    template_id = create.json()["data"]["id"]

    response = await authorized_client.delete(
        f"/cms/email-templates/{template_id}"
    )

    assert response.status_code == 200