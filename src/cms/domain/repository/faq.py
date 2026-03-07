from abc import ABC
from typing import Optional

from src.cms.domain.aggregates.faq import FaqAggregate


class FaqRepository(ABC):
    """Интерфейс репозитория для FAQ."""

    async def get_by_id(self, faq_id: int) -> Optional[FaqAggregate]:
        """Получить FAQ по ID."""
        ...

    async def get_all(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> list[FaqAggregate]:
        """Получить все FAQ с фильтрацией."""
        ...

    async def create(self, aggregate: FaqAggregate) -> FaqAggregate:
        """Создать FAQ."""
        ...

    async def delete(self, faq_id: int) -> bool:
        """Удалить FAQ."""
        ...

    async def update(self, aggregate: FaqAggregate) -> FaqAggregate:
        """Обновить FAQ."""
        ...
