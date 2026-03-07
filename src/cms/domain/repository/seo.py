from abc import ABC
from typing import Optional

from src.cms.domain.aggregates.seo import SeoAggregate


class SeoRepository(ABC):
    """Интерфейс репозитория для SEO данных."""

    async def get_by_id(self, seo_id: int) -> Optional[SeoAggregate]:
        """Получить SEO по ID."""
        ...

    async def get_by_page_slug(self, page_slug: str) -> Optional[SeoAggregate]:
        """Получить SEO по slug страницы."""
        ...

    async def create(self, aggregate: SeoAggregate) -> SeoAggregate:
        """Создать SEO запись."""
        ...

    async def delete(self, seo_id: int) -> bool:
        """Удалить SEO запись."""
        ...

    async def update(self, aggregate: SeoAggregate) -> SeoAggregate:
        """Обновить SEO запись."""
        ...
