import pytest


@pytest.mark.asyncio
async def test_create_faq_200(authorized_client):

    response = await authorized_client.post(
        "/cms/faq",
        json={
            "question": "Как купить?",
            "answer": "Добавьте товар в корзину",
            "category": "general"
        }
    )

    assert response.status_code == 200
    assert response.json()["data"]["question"] == "Как купить?"


@pytest.mark.asyncio
async def test_update_faq_200(authorized_client):

    create = await authorized_client.post(
        "/cms/faq",
        json={
            "question": "Test",
            "answer": "Test"
        }
    )

    faq_id = create.json()["data"]["id"]

    response = await authorized_client.patch(
        f"/cms/faq/{faq_id}",
        json={"answer": "Updated"}
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_faq_200(authorized_client):

    create = await authorized_client.post(
        "/cms/faq",
        json={
            "question": "Delete",
            "answer": "Delete"
        }
    )

    faq_id = create.json()["data"]["id"]

    response = await authorized_client.delete(
        f"/cms/faq/{faq_id}"
    )

    assert response.status_code == 200