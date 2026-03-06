from abc import ABC
from typing import Optional

from src.catalog.product.domain.aggregates.product import ProductAggregate
from src.catalog.product.domain.events.product_events import DomainEvent


class ProductRepository(ABC):

    async def get(self, product_id: int) -> Optional[ProductAggregate]:
        ...

    async def get_by_name(self, name: str) -> Optional[ProductAggregate]:
        ...

    async def create(self, aggregate: ProductAggregate) -> ProductAggregate:
        """Создать продукт. После вызова доступны события через aggregate.get_events()."""
        ...

    async def update(self, aggregate: ProductAggregate) -> ProductAggregate:
        """Обновить продукт. После вызова доступны события через aggregate.get_events()."""
        ...

    async def delete(self, product_id: int) -> bool:
        ...

    async def get_related_by_filterable_attributes(
        self,
        product_id: int,
        category_id: Optional[int],
    ) -> list[ProductAggregate]:
        ...
