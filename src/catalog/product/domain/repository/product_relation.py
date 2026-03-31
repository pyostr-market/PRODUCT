from abc import ABC
from typing import List, Optional

from src.catalog.product.domain.aggregates.product_relation import ProductRelationAggregate


class ProductRelationRepository(ABC):
    """Репозиторий для связей между товарами."""

    async def get(self, relation_id: int) -> Optional[ProductRelationAggregate]:
        """Получить связь по ID."""
        ...

    async def get_by_product(
        self,
        product_id: int,
        relation_type: Optional[str] = None,
    ) -> List[ProductRelationAggregate]:
        """Получить все связи для товара (опционально по типу)."""
        ...

    async def exists(
        self,
        product_id: int,
        related_product_id: int,
        relation_type: str,
    ) -> bool:
        """Проверить существование связи."""
        ...

    async def create(self, aggregate: ProductRelationAggregate) -> ProductRelationAggregate:
        """Создать связь."""
        ...

    async def update(self, aggregate: ProductRelationAggregate) -> ProductRelationAggregate:
        """Обновить связь."""
        ...

    async def delete(self, relation_id: int) -> bool:
        """Удалить связь по ID."""
        ...
