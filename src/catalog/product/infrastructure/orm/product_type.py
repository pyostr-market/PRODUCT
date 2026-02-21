from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.domain.exceptions import ProductTypeNotFound
from src.catalog.product.domain.repository.product_type import ProductTypeRepository
from src.catalog.product.infrastructure.models.product_type import ProductType


class SqlAlchemyProductTypeRepository(ProductTypeRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, product_type_id: int) -> Optional[ProductTypeAggregate]:
        model = await self.db.get(ProductType, product_type_id)
        if not model:
            return None
        return self._to_aggregate(model)

    async def get_by_name(self, name: str) -> Optional[ProductTypeAggregate]:
        stmt = select(ProductType).where(ProductType.name == name)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_aggregate(model)

    async def create(self, aggregate: ProductTypeAggregate) -> ProductTypeAggregate:
        model = ProductType(
            name=aggregate.name,
            parent_id=aggregate.parent_id,
        )
        self.db.add(model)
        await self.db.flush()
        aggregate._set_id(model.id)
        return aggregate

    async def update(self, aggregate: ProductTypeAggregate) -> ProductTypeAggregate:
        model = await self.db.get(ProductType, aggregate.id)
        if not model:
            raise ProductTypeNotFound()
        model.name = aggregate.name
        model.parent_id = aggregate.parent_id
        await self.db.flush()
        return aggregate

    async def delete(self, product_type_id: int) -> bool:
        model = await self.db.get(ProductType, product_type_id)
        if not model:
            return False
        await self.db.delete(model)
        return True

    @staticmethod
    def _to_aggregate(model: ProductType) -> ProductTypeAggregate:
        return ProductTypeAggregate(
            product_type_id=model.id,
            name=model.name,
            parent_id=model.parent_id,
        )
