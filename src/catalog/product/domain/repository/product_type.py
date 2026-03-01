from typing import Optional

from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate


class ProductTypeRepository:

    async def get(self, product_type_id: int) -> Optional[ProductTypeAggregate]:
        raise NotImplementedError

    async def get_by_name(self, name: str) -> Optional[ProductTypeAggregate]:
        raise NotImplementedError

    async def create(self, aggregate: ProductTypeAggregate) -> ProductTypeAggregate:
        raise NotImplementedError

    async def update(self, aggregate: ProductTypeAggregate) -> ProductTypeAggregate:
        raise NotImplementedError

    async def delete(self, product_type_id: int) -> bool:
        raise NotImplementedError
