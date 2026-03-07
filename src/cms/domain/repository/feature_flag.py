from abc import ABC
from typing import Optional

from src.cms.domain.aggregates.feature_flag import FeatureFlagAggregate


class FeatureFlagRepository(ABC):
    """Интерфейс репозитория для feature flags."""

    async def get_by_id(self, flag_id: int) -> Optional[FeatureFlagAggregate]:
        """Получить flag по ID."""
        ...

    async def get_by_key(self, key: str) -> Optional[FeatureFlagAggregate]:
        """Получить flag по ключу."""
        ...

    async def get_all(self) -> list[FeatureFlagAggregate]:
        """Получить все flags."""
        ...

    async def create(self, aggregate: FeatureFlagAggregate) -> FeatureFlagAggregate:
        """Создать flag."""
        ...

    async def delete(self, flag_id: int) -> bool:
        """Удалить flag."""
        ...

    async def update(self, aggregate: FeatureFlagAggregate) -> FeatureFlagAggregate:
        """Обновить flag."""
        ...
