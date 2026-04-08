"""
Тесты для DeleteRegionCommand.

Проверяют HTTP endpoints удаления региона.
"""
import pytest


class TestRegionDelete:

    @pytest.mark.asyncio
    async def test_delete_region_success(self, authorized_client):
        """Успешное удаление региона"""
        # Создаем регион
        create_resp = await authorized_client.post(
            "/region",
            json={"name": "Северо-Западный"},
        )
        assert create_resp.status_code == 200
        region_id = create_resp.json()["data"]["id"]

        # Удаляем
        delete_resp = await authorized_client.delete(f"/region/{region_id}")

        assert delete_resp.status_code == 200
        data = delete_resp.json()["data"]
        assert data["deleted"] is True

        # Проверяем, что регион удален
        get_resp = await authorized_client.get(f"/region/{region_id}")
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_region_not_found(self, authorized_client):
        """Удаление несуществующего региона"""
        delete_resp = await authorized_client.delete("/region/99999")

        assert delete_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_region_cascade_children(self, authorized_client):
        """Удаление региона с дочерними регионами (CASCADE на уровне БД)"""
        # Создаем родительский регион
        parent_resp = await authorized_client.post(
            "/region",
            json={"name": "Северо-Западный"},
        )
        assert parent_resp.status_code == 200
        parent_id = parent_resp.json()["data"]["id"]

        # Создаем дочерний регион
        child_resp = await authorized_client.post(
            "/region",
            json={"name": "Санкт-Петербург", "parent_id": parent_id},
        )
        assert child_resp.status_code == 200

        # Удаляем родительский регион
        # SQLAlchemy cascade удалит и дочерние регионы
        delete_resp = await authorized_client.delete(f"/region/{parent_id}")
        assert delete_resp.status_code == 200

        # Проверяем, что родительский регион удален
        get_parent_resp = await authorized_client.get(f"/region/{parent_id}")
        assert get_parent_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_region_unauthorized(self, client):
        """Удаление без авторизации"""
        delete_resp = await client.delete("/region/1")

        assert delete_resp.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_region_no_permissions(self, authorized_client_no_perms):
        """Удаление без прав"""
        delete_resp = await authorized_client_no_perms.delete("/region/1")

        assert delete_resp.status_code == 403
