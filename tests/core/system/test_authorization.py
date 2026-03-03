"""Тесты для AuthorizationApiClient и PermissionCacheService."""

import pytest
import httpx
from httpx import Request, Response

from src.core.system.authorizationApi import (
    AuthorizationApiClient,
    AuthorizationApiError,
    Permission,
)
from src.core.system.permission_cache import PermissionCacheService


class TestPermissionCacheService:
    """Тесты для сервиса кэширования прав."""

    @pytest.mark.asyncio
    async def test_get_returns_none_when_key_not_in_cache(self):
        cache = PermissionCacheService()
        result = await cache.get(user_id=1, token_version="1")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_returns_permissions(self):
        cache = PermissionCacheService()
        permissions = [Permission(id=1, name="permission:view")]

        await cache.set(user_id=1, token_version="1", permissions=permissions)
        result = await cache.get(user_id=1, token_version="1")

        assert result == permissions

    @pytest.mark.asyncio
    async def test_set_deletes_old_user_versions(self):
        cache = PermissionCacheService()
        permissions_v1 = [Permission(id=1, name="permission:view")]
        permissions_v2 = [Permission(id=2, name="permission:create")]

        await cache.set(user_id=1, token_version="1", permissions=permissions_v1)
        await cache.set(user_id=1, token_version="2", permissions=permissions_v2)

        # Старая версия должна быть удалена
        result_v1 = await cache.get(user_id=1, token_version="1")
        result_v2 = await cache.get(user_id=1, token_version="2")

        assert result_v1 is None
        assert result_v2 == permissions_v2

    @pytest.mark.asyncio
    async def test_different_users_are_cached_separately(self):
        cache = PermissionCacheService()
        permissions_user1 = [Permission(id=1, name="permission:view")]
        permissions_user2 = [Permission(id=2, name="permission:create")]

        await cache.set(user_id=1, token_version="1", permissions=permissions_user1)
        await cache.set(user_id=2, token_version="1", permissions=permissions_user2)

        result_user1 = await cache.get(user_id=1, token_version="1")
        result_user2 = await cache.get(user_id=2, token_version="1")

        assert result_user1 == permissions_user1
        assert result_user2 == permissions_user2

    @pytest.mark.asyncio
    async def test_delete_removes_entry(self):
        cache = PermissionCacheService()
        permissions = [Permission(id=1, name="permission:view")]

        await cache.set(user_id=1, token_version="1", permissions=permissions)
        await cache.delete(user_id=1, token_version="1")

        result = await cache.get(user_id=1, token_version="1")
        assert result is None

    @pytest.mark.asyncio
    async def test_clear_removes_all_entries(self):
        cache = PermissionCacheService()

        await cache.set(user_id=1, token_version="1", permissions=[Permission(id=1, name="view")])
        await cache.set(user_id=2, token_version="1", permissions=[Permission(id=2, name="create")])

        await cache.clear()

        stats = await cache.get_stats()
        assert stats["entries_count"] == 0

    @pytest.mark.asyncio
    async def test_get_stats_returns_correct_counts(self):
        cache = PermissionCacheService()

        await cache.set(user_id=1, token_version="1", permissions=[Permission(id=1, name="view")])
        await cache.set(user_id=1, token_version="2", permissions=[Permission(id=2, name="create")])
        await cache.set(user_id=2, token_version="1", permissions=[Permission(id=3, name="delete")])

        stats = await cache.get_stats()

        assert stats["entries_count"] == 2  # v1 удалена, остались v2 для user1 и v1 для user2
        assert stats["unique_users"] == 2


class TestAuthorizationApiClient:
    """Тесты для клиента API авторизации."""

    def _create_client_with_mock(self, mock_handler):
        """Создать клиент с mock-транспортом."""
        http_client = httpx.AsyncClient(
            base_url="https://market-user.open-gpt.ru",
            transport=httpx.MockTransport(mock_handler),
        )
        return AuthorizationApiClient(http_client=http_client)

    @pytest.mark.asyncio
    async def test_get_user_permissions_success(self):
        """Тест успешного получения прав."""

        def mock_handler(request: Request):
            return Response(
                status_code=200,
                json={
                    "success": True,
                    "data": [
                        {"id": 1, "name": "permission:view"},
                        {"id": 3, "name": "permission:create"},
                    ],
                },
            )

        client = self._create_client_with_mock(mock_handler)
        try:
            permissions = await client.get_user_permissions("test-token")

            assert len(permissions) == 2
            assert permissions[0].id == 1
            assert permissions[0].name == "permission:view"
            assert permissions[1].id == 3
            assert permissions[1].name == "permission:create"
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_user_permissions_empty_data(self):
        """Тест с пустым списком прав."""

        def mock_handler(request: Request):
            return Response(
                status_code=200,
                json={"success": True, "data": []},
            )

        client = self._create_client_with_mock(mock_handler)
        try:
            permissions = await client.get_user_permissions("test-token")
            assert permissions == []
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_user_permissions_401(self):
        """Тест с 401 ошибкой."""

        def mock_handler(request: Request):
            return Response(status_code=401)

        client = self._create_client_with_mock(mock_handler)
        try:
            with pytest.raises(AuthorizationApiError) as exc_info:
                await client.get_user_permissions("invalid-token")
            assert exc_info.value.status_code == 401
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_user_permissions_403(self):
        """Тест с 403 ошибкой."""

        def mock_handler(request: Request):
            return Response(status_code=403)

        client = self._create_client_with_mock(mock_handler)
        try:
            with pytest.raises(AuthorizationApiError) as exc_info:
                await client.get_user_permissions("test-token")
            assert exc_info.value.status_code == 403
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_user_permissions_500(self):
        """Тест с 500 ошибкой сервера."""

        def mock_handler(request: Request):
            return Response(status_code=500)

        client = self._create_client_with_mock(mock_handler)
        try:
            with pytest.raises(AuthorizationApiError) as exc_info:
                await client.get_user_permissions("test-token")
            assert exc_info.value.status_code == 401
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_user_permissions_success_false(self):
        """Тест когда API вернул success=false."""

        def mock_handler(request: Request):
            return Response(
                status_code=200,
                json={"success": False, "data": []},
            )

        client = self._create_client_with_mock(mock_handler)
        try:
            with pytest.raises(AuthorizationApiError) as exc_info:
                await client.get_user_permissions("test-token")
            assert exc_info.value.status_code == 401
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_user_permissions_sends_authorization_header(self):
        """Тест что заголовок Authorization передаётся корректно."""

        received_headers = {}

        def mock_handler(request: Request):
            received_headers.update(dict(request.headers))
            return Response(
                status_code=200,
                json={"success": True, "data": []},
            )

        client = self._create_client_with_mock(mock_handler)
        try:
            await client.get_user_permissions("my-test-token")
            assert "authorization" in received_headers
            assert received_headers["authorization"] == "Bearer my-test-token"
        finally:
            await client.close()
