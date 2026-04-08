"""
Тесты для CreateRegionCommand.

Проверяют HTTP endpoints создания региона.
"""
import pytest


# =========================================================
# Создание региона
# =========================================================

class TestRegionCreate:

    @pytest.mark.asyncio
    async def test_create_region_success(self, authorized_client):
        """Успешное создание региона"""
        response = await authorized_client.post(
            "/region",
            json={
                "name": "Северо-Западный",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Северо-Западный"
        assert data["data"]["parent_id"] is None

    @pytest.mark.asyncio
    async def test_create_region_with_parent(self, authorized_client):
        """Создание региона с родителем"""
        # Создаем родительский регион
        parent_response = await authorized_client.post(
            "/region",
            json={"name": "Северо-Западный"},
        )
        assert parent_response.status_code == 200
        parent_id = parent_response.json()["data"]["id"]

        # Создаем дочерний регион
        child_response = await authorized_client.post(
            "/region",
            json={
                "name": "Санкт-Петербург",
                "parent_id": parent_id,
            },
        )

        assert child_response.status_code == 200
        data = child_response.json()["data"]
        assert data["name"] == "Санкт-Петербург"
        assert data["parent_id"] == parent_id

    @pytest.mark.asyncio
    async def test_create_region_name_too_short(self, authorized_client):
        """Имя слишком короткое"""
        response = await authorized_client.post(
            "/region",
            json={"name": "А"},
        )

        assert response.status_code == 400  # Domain validation

    @pytest.mark.asyncio
    async def test_create_region_name_empty(self, authorized_client):
        """Пустое имя"""
        response = await authorized_client.post(
            "/region",
            json={"name": ""},
        )

        assert response.status_code == 400  # Domain validation

    @pytest.mark.asyncio
    async def test_create_region_duplicate_name(self, authorized_client):
        """Дубликат имени региона"""
        response1 = await authorized_client.post(
            "/region",
            json={"name": "Северо-Западный"},
        )
        assert response1.status_code == 200

        response2 = await authorized_client.post(
            "/region",
            json={"name": "Северо-Западный"},
        )
        assert response2.status_code == 409

    @pytest.mark.asyncio
    async def test_create_region_name_trimmed(self, authorized_client):
        """Имя обрезается"""
        response = await authorized_client.post(
            "/region",
            json={"name": "  Северо-Западный  "},
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Северо-Западный"

    @pytest.mark.asyncio
    async def test_create_region_cyrillic_name(self, authorized_client):
        """Кириллическое имя"""
        response = await authorized_client.post(
            "/region",
            json={"name": "Центральный федеральный округ"},
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "Центральный федеральный округ"

    @pytest.mark.asyncio
    async def test_create_region_unauthorized(self, client):
        """Создание без авторизации"""
        response = await client.post(
            "/region",
            json={"name": "Северо-Западный"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_region_no_permissions(self, authorized_client_no_perms):
        """Создание без прав"""
        response = await authorized_client_no_perms.post(
            "/region",
            json={"name": "Северо-Западный"},
        )

        assert response.status_code == 403
