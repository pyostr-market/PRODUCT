from typing import Optional

from src.catalog.product.domain.aggregates.product import ProductAttributeAggregate


class ProductAttributeRepository:

    async def get(self, attribute_id: int) -> Optional[ProductAttributeAggregate]:
        raise NotImplementedError

    async def get_by_name(self, name: str) -> Optional[ProductAttributeAggregate]:
        raise NotImplementedError

    async def create(self, aggregate: ProductAttributeAggregate) -> ProductAttributeAggregate:
        raise NotImplementedError

    async def update(self, aggregate: ProductAttributeAggregate) -> ProductAttributeAggregate:
        raise NotImplementedError

    async def delete(self, attribute_id: int) -> bool:
        raise NotImplementedError
