from abc import ABC
from typing import Optional

from src.cms.domain.aggregates.page import PageAggregate


class PageRepository(ABC):
    """Интерфейс репозитория для страниц."""

    async def get_by_id(self, page_id: int) -> Optional[PageAggregate]:
        """Получить страницу по ID."""
        ...

    async def get_by_slug(self, slug: str) -> Optional[PageAggregate]:
        """Получить страницу по slug."""
        ...

    async def create(self, aggregate: PageAggregate) -> PageAggregate:
        """Создать страницу."""
        ...

    async def delete(self, page_id: int) -> bool:
        """Удалить страницу."""
        ...

    async def update(self, aggregate: PageAggregate) -> PageAggregate:
        """Обновить страницу."""
        ...

    async def exists_by_slug(self, slug: str, exclude_id: Optional[int] = None) -> bool:
        """Проверить существование страницы с данным slug."""
        ...
