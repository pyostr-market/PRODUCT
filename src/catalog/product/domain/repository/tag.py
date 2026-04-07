from abc import ABC, abstractmethod
from typing import List, Optional

from src.catalog.product.domain.aggregates.tag import TagAggregate


class TagRepositoryInterface(ABC):
    """Интерфейс репозитория для работы с тегами."""

    @abstractmethod
    async def create(self, tag: TagAggregate) -> TagAggregate:
        """Создать новый тег."""
        pass

    @abstractmethod
    async def get_by_id(self, tag_id: int) -> Optional[TagAggregate]:
        """Получить тег по ID."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[TagAggregate]:
        """Получить тег по имени."""
        pass

    @abstractmethod
    async def update(self, tag: TagAggregate) -> TagAggregate:
        """Обновить тег."""
        pass

    @abstractmethod
    async def delete(self, tag_id: int) -> None:
        """Удалить тег."""
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[TagAggregate]:
        """Получить все теги с пагинацией."""
        pass
