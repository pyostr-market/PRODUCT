"""Тесты для Email Templates (Commands и Queries)."""

import pytest

from src.cms.api.schemas.email_template_schemas import EmailTemplateReadSchema


@pytest.mark.asyncio
async def test_create_email_template_200(authorized_client):
    """Тест успешного создания email шаблона."""
    response = await authorized_client.post(
        "/cms/email-templates/admin",
        json={
            "key": "password_reset",
            "subject": "Восстановление пароля",
            "body_html": "<p>Ссылка: {{reset_link}}</p>",
            "body_text": "Ссылка: {{reset_link}}",
            "variables": ["reset_link"],
            "is_active": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    template = EmailTemplateReadSchema(**body["data"])
    assert template.key == "password_reset"
    assert template.subject == "Восстановление пароля"
    assert template.variables == ["reset_link"]


@pytest.mark.asyncio
async def test_create_email_template_400_key_already_exists(authorized_client):
    """Тест создания шаблона с существующим ключом."""
    # Создаём первый шаблон
    await authorized_client.post(
        "/cms/email-templates/admin",
        json={
            "key": "welcome",
            "subject": "Welcome",
            "body_html": "<p>Hello</p>",
        },
    )

    # Пытаемся создать второй с таким же ключом
    response = await authorized_client.post(
        "/cms/email-templates/admin",
        json={
            "key": "welcome",
            "subject": "Welcome 2",
            "body_html": "<p>Hello 2</p>",
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_create_email_template_400_invalid_key(authorized_client):
    """Тест создания шаблона с некорректным ключом."""
    response = await authorized_client.post(
        "/cms/email-templates/admin",
        json={
            "key": "123invalid",  # Должен начинаться с буквы
            "subject": "Test",
            "body_html": "<p>Test</p>",
        },
    )

    # Pydantic валидация возвращает 422
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_email_template_200(authorized_client):
    """Тест успешного обновления шаблона."""
    # Создаём шаблон
    create_response = await authorized_client.post(
        "/cms/email-templates/admin",
        json={
            "key": "order_confirm",
            "subject": "Old Subject",
            "body_html": "<p>Old</p>",
        },
    )
    assert create_response.status_code == 200
    template_id = create_response.json()["data"]["id"]

    # Обновляем шаблон
    update_response = await authorized_client.put(
        f"/cms/email-templates/admin/{template_id}",
        json={
            "subject": "New Subject",
            "body_html": "<p>New</p>",
            "body_text": "New text",
            "variables": ["order_id"],
            "is_active": False,
        },
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["success"] is True

    template = EmailTemplateReadSchema(**body["data"])
    assert template.subject == "New Subject"
    assert template.body_text == "New text"
    assert template.is_active is False


@pytest.mark.asyncio
async def test_update_email_template_404_not_found(authorized_client):
    """Тест обновления несуществующего шаблона."""
    response = await authorized_client.put(
        "/cms/email-templates/admin/999999",
        json={"subject": "New"},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_delete_email_template_200(authorized_client):
    """Тест успешного удаления шаблона."""
    # Создаём шаблон
    create_response = await authorized_client.post(
        "/cms/email-templates/admin",
        json={
            "key": "to_delete",
            "subject": "ToDelete",
            "body_html": "<p>Delete</p>",
        },
    )
    assert create_response.status_code == 200
    template_id = create_response.json()["data"]["id"]

    # Удаляем шаблон
    delete_response = await authorized_client.delete(
        f"/cms/email-templates/admin/{template_id}"
    )

    assert delete_response.status_code == 200
    body = delete_response.json()
    assert body["success"] is True


@pytest.mark.asyncio
async def test_delete_email_template_404_not_found(authorized_client):
    """Тест удаления несуществующего шаблона."""
    response = await authorized_client.delete(
        "/cms/email-templates/admin/999999"
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_get_email_template_by_key_200(authorized_client, client):
    """Тест получения шаблона по ключу."""
    # Создаём шаблон
    await authorized_client.post(
        "/cms/email-templates/admin",
        json={
            "key": "verification",
            "subject": "Verify Email",
            "body_html": "<p>Verify</p>",
        },
    )

    # Получаем шаблон
    response = await client.get("/cms/email-templates/verification")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["key"] == "verification"


@pytest.mark.asyncio
async def test_get_email_template_404_not_found(client):
    """Тест получения несуществующего шаблона."""
    response = await client.get("/cms/email-templates/nonexistent")

    assert response.status_code == 404
    body = response.json()
    # Проверяем что ответ содержит ошибку
    assert "error" in body or body.get("success") is False


@pytest.mark.asyncio
async def test_get_all_email_templates_200(authorized_client, client):
    """Тест получения всех шаблонов."""
    # Создаём несколько шаблонов
    await authorized_client.post(
        "/cms/email-templates/admin",
        json={"key": "template1", "subject": "S1", "body_html": "<p>1</p>"},
    )
    await authorized_client.post(
        "/cms/email-templates/admin",
        json={"key": "template2", "subject": "S2", "body_html": "<p>2</p>"},
    )

    # Получаем все шаблоны
    response = await client.get("/cms/email-templates")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 2
