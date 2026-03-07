"""Тесты для Feature Flags (Commands и Queries)."""

import pytest

from src.cms.api.schemas.feature_flag_schemas import FeatureFlagReadSchema


@pytest.mark.asyncio
async def test_create_feature_flag_200(authorized_client):
    """Тест успешного создания feature flag."""
    response = await authorized_client.post(
        "/cms/feature-flags/admin",
        json={
            "key": "chat_enabled",
            "enabled": True,
            "description": "Включение чата поддержки",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    flag = FeatureFlagReadSchema(**body["data"])
    assert flag.key == "chat_enabled"
    assert flag.enabled is True
    assert flag.description == "Включение чата поддержки"


@pytest.mark.asyncio
async def test_create_feature_flag_200_disabled(authorized_client):
    """Тест создания выключенного feature flag."""
    response = await authorized_client.post(
        "/cms/feature-flags/admin",
        json={
            "key": "beta_feature",
            "enabled": False,
            "description": "Бета функция",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    flag = FeatureFlagReadSchema(**body["data"])
    assert flag.key == "beta_feature"
    assert flag.enabled is False


@pytest.mark.asyncio
async def test_create_feature_flag_400_key_already_exists(authorized_client):
    """Тест создания flag с существующим ключом."""
    # Создаём первый flag
    await authorized_client.post(
        "/cms/feature-flags/admin",
        json={"key": "duplicate", "enabled": True},
    )

    # Пытаемся создать второй с таким же ключом
    response = await authorized_client.post(
        "/cms/feature-flags/admin",
        json={"key": "duplicate", "enabled": False},
    )

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_create_feature_flag_400_invalid_key(authorized_client):
    """Тест создания flag с некорректным ключом."""
    response = await authorized_client.post(
        "/cms/feature-flags/admin",
        json={
            "key": "123invalid",  # Должен начинаться с буквы
            "enabled": True,
        },
    )

    # Pydantic валидация возвращает 422
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_feature_flag_200(authorized_client):
    """Тест успешного обновления feature flag."""
    # Создаём flag
    create_response = await authorized_client.post(
        "/cms/feature-flags/admin",
        json={"key": "test_flag", "enabled": False, "description": "Old desc"},
    )
    assert create_response.status_code == 200
    flag_id = create_response.json()["data"]["id"]

    # Обновляем flag
    update_response = await authorized_client.put(
        f"/cms/feature-flags/admin/{flag_id}",
        json={
            "enabled": True,
            "description": "New desc",
        },
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["success"] is True

    flag = FeatureFlagReadSchema(**body["data"])
    assert flag.enabled is True
    assert flag.description == "New desc"


@pytest.mark.asyncio
async def test_update_feature_flag_404_not_found(authorized_client):
    """Тест обновления несуществующего flag."""
    response = await authorized_client.put(
        "/cms/feature-flags/admin/999999",
        json={"enabled": True},
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_delete_feature_flag_200(authorized_client):
    """Тест успешного удаления feature flag."""
    # Создаём flag
    create_response = await authorized_client.post(
        "/cms/feature-flags/admin",
        json={"key": "to_delete", "enabled": True},
    )
    assert create_response.status_code == 200
    flag_id = create_response.json()["data"]["id"]

    # Удаляем flag
    delete_response = await authorized_client.delete(
        f"/cms/feature-flags/admin/{flag_id}"
    )

    assert delete_response.status_code == 200
    body = delete_response.json()
    assert body["success"] is True


@pytest.mark.asyncio
async def test_delete_feature_flag_404_not_found(authorized_client):
    """Тест удаления несуществующего flag."""
    response = await authorized_client.delete(
        "/cms/feature-flags/admin/999999"
    )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_get_all_feature_flags_200(authorized_client, client):
    """Тест получения всех feature flags."""
    # Создаём несколько flags
    await authorized_client.post(
        "/cms/feature-flags/admin",
        json={"key": "flag1", "enabled": True},
    )
    await authorized_client.post(
        "/cms/feature-flags/admin",
        json={"key": "flag2", "enabled": False},
    )

    # Получаем все flags
    response = await client.get("/cms/feature-flags")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 2


@pytest.mark.asyncio
async def test_get_enabled_flags_200(authorized_client, client):
    """Тест получения только включенных flags."""
    # Создаём включенный и выключенный flags
    await authorized_client.post(
        "/cms/feature-flags/admin",
        json={"key": "enabled_flag", "enabled": True},
    )
    await authorized_client.post(
        "/cms/feature-flags/admin",
        json={"key": "disabled_flag", "enabled": False},
    )

    # Получаем только включенные
    response = await client.get("/cms/feature-flags/enabled")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    enabled_flags = body["data"]["enabled_flags"]
    assert "enabled_flag" in enabled_flags
    assert "disabled_flag" not in enabled_flags


@pytest.mark.asyncio
async def test_toggle_feature_flag(authorized_client):
    """Тест переключения состояния feature flag."""
    # Создаём выключенный flag
    create_response = await authorized_client.post(
        "/cms/feature-flags/admin",
        json={"key": "toggle_flag", "enabled": False},
    )
    flag_id = create_response.json()["data"]["id"]

    # Включаем
    update_response = await authorized_client.put(
        f"/cms/feature-flags/admin/{flag_id}",
        json={"enabled": True},
    )
    assert update_response.json()["data"]["enabled"] is True

    # Выключаем
    update_response2 = await authorized_client.put(
        f"/cms/feature-flags/admin/{flag_id}",
        json={"enabled": False},
    )
    assert update_response2.json()["data"]["enabled"] is False
