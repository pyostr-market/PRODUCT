from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.domain.aggregates.product import ProductAttributeAggregate
from src.catalog.product.domain.exceptions import ProductAttributeNotFound
from src.catalog.product.domain.repository.product_attribute import ProductAttributeRepository
from src.catalog.product.infrastructure.models.product_attribute import ProductAttribute


class SqlAlchemyProductAttributeRepository(ProductAttributeRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, attribute_id: int) -> Optional[ProductAttributeAggregate]:
        model = await self.db.get(ProductAttribute, attribute_id)
        if not model:
            return None
        return self._to_aggregate(model)

    async def get_by_name(self, name: str) -> Optional[ProductAttributeAggregate]:
        stmt = select(ProductAttribute).where(ProductAttribute.name == name)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_aggregate(model)

    async def create(self, aggregate: ProductAttributeAggregate) -> ProductAttributeAggregate:
        model = ProductAttribute(
            name=aggregate.name,
            is_filterable=aggregate.is_filterable,
        )
        self.db.add(model)
        await self.db.flush()
        aggregate._set_id(model.id)
        return aggregate

    async def update(self, aggregate: ProductAttributeAggregate) -> ProductAttributeAggregate:
        model = await self.db.get(ProductAttribute, aggregate.id)
        if not model:
            raise ProductAttributeNotFound()
        model.name = aggregate.name
        model.is_filterable = aggregate.is_filterable
        await self.db.flush()
        return aggregate

    async def delete(self, attribute_id: int) -> bool:
        model = await self.db.get(ProductAttribute, attribute_id)
        if not model:
            return False
        await self.db.delete(model)
        return True

    @staticmethod
    def _to_aggregate(model: ProductAttribute) -> ProductAttributeAggregate:
        return ProductAttributeAggregate(
            attribute_id=model.id,
            name=model.name,
            value="",
            is_filterable=model.is_filterable,
        )
