import time
from dataclasses import dataclass, field

from src.core.system.authorizationApi.schemas import Permission


@dataclass
class CachedPermissions:
    permissions: list[Permission]
    created_at: float = field(default_factory=time.time)


class PermissionCacheService:
    """
    In-memory сервис для кэширования прав пользователя.

    Ключ кэша формируется как: {user_id}:{token_version}

    При смене версии токена старые записи удаляются.
    """

    def __init__(self):
        self._store: dict[str, CachedPermissions] = {}

    def _make_key(self, user_id: int, token_version: str) -> str:
        return f"{user_id}:{token_version}"

    async def get(
        self, user_id: int, token_version: str
    ) -> list[Permission] | None:
        """
        Получить права из кэша по userId и версии токена.

        Returns:
            Список прав или None, если в кэше нет записи.
        """
        key = self._make_key(user_id, token_version)
        cached = self._store.get(key)

        if cached is None:
            return None

        return cached.permissions

    async def set(
        self,
        user_id: int,
        token_version: str,
        permissions: list[Permission],
    ) -> None:
        """
        Сохранить права в кэш.

        Перед сохранением удаляет все старые записи этого пользователя.
        """
        # Удаляем старые записи этого пользователя (с другими версиями)
        await self._delete_user_entries(user_id)

        key = self._make_key(user_id, token_version)
        self._store[key] = CachedPermissions(
            permissions=permissions,
            created_at=time.time(),
        )

    async def _delete_user_entries(self, user_id: int) -> None:
        """Удалить все записи кэша для указанного пользователя."""
        prefix = f"{user_id}:"
        keys_to_delete = [
            key for key in self._store if key.startswith(prefix)
        ]

        for key in keys_to_delete:
            del self._store[key]

    async def delete(self, user_id: int, token_version: str) -> None:
        """Удалить конкретную запись из кэша."""
        key = self._make_key(user_id, token_version)
        self._store.pop(key, None)

    async def clear(self) -> None:
        """Очистить весь кэш."""
        self._store.clear()

    async def get_stats(self) -> dict:
        """Получить статистику кэша."""
        return {
            "entries_count": len(self._store),
            "unique_users": len(
                {key.split(":")[0] for key in self._store}
            ),
        }
