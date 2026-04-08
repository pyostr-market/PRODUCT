"""
Тесты для UpdateRegionCommand.

Проверяют HTTP endpoints обновления региона.
"""
import pytest


class TestRegionUpdate:

    @pytest.mark.asyncio
    async def test_update_region_name(self, authorized_client):
        """Обновление имени региона"""
        # Создаем регион
        create_resp = await authorized_client.post(
            "/region",
            json={"name": "Северо-Западный"},
        )
        assert create_resp.status_code == 200
        region_id = create_resp.json()["data"]["id"]

        # Обновляем
        update_resp = await authorized_client.put(
            f"/region/{region_id}",
            json={"name": "Северо-Западный федеральный округ"},
        )

        assert update_resp.status_code == 200
        data = update_resp.json()["data"]
        assert data["name"] == "Северо-Западный федеральный округ"

    @pytest.mark.asyncio
    async def test_update_region_parent(self, authorized_client):
        """Обновление родительского региона"""
        # Создаем родительский регион
        parent_resp = await authorized_client.post(
            "/region",
            json={"name": "Северо-Западный"},
        )
        assert parent_resp.status_code == 200
        parent_id = parent_resp.json()["data"]["id"]

        # Создаем дочерний регион без родителя
        child_resp = await authorized_client.post(
            "/region",
            json={"name": "Санкт-Петербург"},
        )
        assert child_resp.status_code == 200
        child_id = child_resp.json()["data"]["id"]

        # Привязываем к родителю
        update_resp = await authorized_client.put(
            f"/region/{child_id}",
            json={"parent_id": parent_id},
        )

        assert update_resp.status_code == 200
        data = update_resp.json()["data"]
        assert data["parent_id"] == parent_id

    @pytest.mark.asyncio
    async def test_update_region_not_found(self, authorized_client):
        """Обновление несуществующего региона"""
        update_resp = await authorized_client.put(
            "/region/99999",
            json={"name": "Новое имя"},
        )

        assert update_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_region_name_too_short(self, authorized_client):
        """Обновление на слишком короткое имя"""
        create_resp = await authorized_client.post(
            "/region",
            json={"name": "Северо-Западный"},
        )
        assert create_resp.status_code == 200
        region_id = create_resp.json()["data"]["id"]

        update_resp = await authorized_client.put(
            f"/region/{region_id}",
            json={"name": "А"},
        )

        assert update_resp.status_code == 400  # Domain validation

    @pytest.mark.asyncio
    async def test_update_region_partial(self, authorized_client):
        """Частичное обновление (только имя)"""
        create_resp = await authorized_client.post(
            "/region",
            json={"name": "Северо-Западный", "parent_id": None},
        )
        assert create_resp.status_code == 200
        region_id = create_resp.json()["data"]["id"]

        update_resp = await authorized_client.put(
            f"/region/{region_id}",
            json={"name": "Северо-Западный ФО"},  # только имя
        )

        assert update_resp.status_code == 200
        data = update_resp.json()["data"]
        assert data["name"] == "Северо-Западный ФО"

    @pytest.mark.asyncio
    async def test_update_region_unauthorized(self, client):
        """Обновление без авторизации"""
        update_resp = await client.put(
            "/region/1",
            json={"name": "Новое имя"},
        )

        assert update_resp.status_code == 401

    @pytest.mark.asyncio
    async def test_update_region_no_permissions(self, authorized_client_no_perms):
        """Обновление без прав"""
        update_resp = await authorized_client_no_perms.put(
            "/region/1",
            json={"name": "Новое имя"},
        )

        assert update_resp.status_code == 403
