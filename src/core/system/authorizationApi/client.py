import httpx

from src.core.system.authorizationApi.schemas import Permission


class AuthorizationApiClient:
    """Клиент для получения прав пользователя через системный API."""

    BASE_URL = "https://market-user.open-gpt.ru"

    def __init__(self, http_client: httpx.AsyncClient | None = None):
        self._client = http_client or httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=10.0,
        )

    async def get_user_permissions(self, token: str) -> list[Permission]:
        """
        Получает права пользователя через внешний API авторизации.

        Args:
            token: JWT-токен пользователя

        Returns:
            Список прав пользователя

        Raises:
            AuthorizationApiError: Если API вернул ошибку или недоступен
        """
        response = await self._client.get(
            "/permissions/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 401:
            raise AuthorizationApiError("Невалидный токен", status_code=401)

        if response.status_code == 403:
            raise AuthorizationApiError("Доступ запрещён", status_code=403)

        if response.status_code != 200:
            raise AuthorizationApiError(
                f"API авторизации вернул ошибку: {response.status_code}",
                status_code=401,
            )

        data = response.json()

        if not data.get("success"):
            raise AuthorizationApiError(
                "API авторизации вернул success=false",
                status_code=401,
            )

        return [
            Permission(id=item["id"], name=item["name"])
            for item in data.get("data", [])
        ]

    async def close(self):
        await self._client.aclose()


class AuthorizationApiError(Exception):
    """Ошибка при обращении к API авторизации."""

    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
