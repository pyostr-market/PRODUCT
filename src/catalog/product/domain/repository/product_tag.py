from abc import ABC, abstractmethod
from typing import List, Optional

from src.catalog.product.domain.aggregates.product_tag import ProductTagAggregate


class ProductTagRepositoryInterface(ABC):
    """Интерфейс репозитория для управления связями товаров с тегами."""

    @abstractmethod
    async def get(self, link_id: int) -> Optional[ProductTagAggregate]:
        """Получить связь по ID."""
        pass

    @abstractmethod
    async def get_by_product(
        self,
        product_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ProductTagAggregate]:
        """Получить все связи для товара."""
        pass

    @abstractmethod
    async def exists(self, product_id: int, tag_id: int) -> bool:
        """Проверить существование связи."""
        pass

    @abstractmethod
    async def create(self, aggregate: ProductTagAggregate) -> ProductTagAggregate:
        """Создать связь."""
        pass

    @abstractmethod
    async def delete(self, product_id: int, tag_id: int) -> bool:
        """Удалить связь по product_id и tag_id."""
        pass

    @abstractmethod
    async def count_by_product(self, product_id: int) -> int:
        """Получить количество тегов у товара."""
        pass
