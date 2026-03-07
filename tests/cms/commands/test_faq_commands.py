"""Тесты для создания, обновления и удаления FAQ."""

import pytest

from src.cms.api.schemas.faq_schemas import FaqReadSchema


@pytest.mark.asyncio
async def test_create_faq_200(authorized_client):
    """Тест успешного создания FAQ."""
    response = await authorized_client.post(
        "/cms/faq/admin",
        json={
            "question": "Как вернуть товар?",
            "answer": "Возврат возможен в течение 14 дней.",
            "category": "returns",
            "order": 0,
            "is_active": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    faq = FaqReadSchema(**body["data"])
    assert faq.question == "Как вернуть товар?"
    assert faq.answer == "Возврат возможен в течение 14 дней."
    assert faq.category == "returns"
    assert faq.is_active is True


@pytest.mark.asyncio
async def test_create_faq_200_no_category(authorized_client):
    """Тест создания FAQ без категории."""
    response = await authorized_client.post(
        "/cms/faq/admin",
        json={
            "question": "Где мой заказ?",
            "answer": "Проверьте статус в личном кабинете.",
            "order": 0,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    faq = FaqReadSchema(**body["data"])
    assert faq.category is None


@pytest.mark.asyncio
async def test_update_faq_200(authorized_client):
    """Тест успешного обновления FAQ."""
    # Создаём FAQ
    create_response = await authorized_client.post(
        "/cms/faq/admin",
        json={
            "question": "Old question?",
            "answer": "Old answer.",
            "category": "old_category",
        },
    )
    assert create_response.status_code == 200
    faq_id = create_response.json()["data"]["id"]

    # Обновляем FAQ
    update_response = await authorized_client.put(
        f"/cms/faq/admin/{faq_id}",
        json={
            "question": "New question?",
            "answer": "New answer.",
            "category": "new_category",
            "order": 5,
            "is_active": False,
        },
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["success"] is True

    faq = FaqReadSchema(**body["data"])
    assert faq.question == "New question?"
    assert faq.answer == "New answer."
    assert faq.category == "new_category"
    assert faq.order == 5
    assert faq.is_active is False


@pytest.mark.asyncio
async def test_update_faq_404_not_found(authorized_client):
    """Тест обновления несуществующего FAQ."""
    response = await authorized_client.put(
        "/cms/faq/admin/999999",
        json={"question": "New?"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_delete_faq_200(authorized_client):
    """Тест успешного удаления FAQ."""
    # Создаём FAQ
    create_response = await authorized_client.post(
        "/cms/faq/admin",
        json={
            "question": "ToDelete?",
            "answer": "Will be deleted.",
        },
    )
    assert create_response.status_code == 200
    faq_id = create_response.json()["data"]["id"]

    # Удаляем FAQ
    delete_response = await authorized_client.delete(f"/cms/faq/admin/{faq_id}")

    assert delete_response.status_code == 200
    body = delete_response.json()
    assert body["success"] is True
    assert body["data"]["faq_id"] == faq_id


@pytest.mark.asyncio
async def test_delete_faq_404_not_found(authorized_client):
    """Тест удаления несуществующего FAQ."""
    response = await authorized_client.delete("/cms/faq/admin/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_create_faq_400_question_too_short(authorized_client):
    """Тест создания FAQ с коротким вопросом."""
    response = await authorized_client.post(
        "/cms/faq/admin",
        json={
            "question": "A",
            "answer": "Answer",
        },
    )

    # Pydantic валидация возвращает 422
    assert response.status_code == 422
