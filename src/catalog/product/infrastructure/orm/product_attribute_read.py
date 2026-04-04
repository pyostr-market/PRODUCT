from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.application.dto.product_attribute import (
    ProductAttributeReadDTO,
)
from src.catalog.product.domain.repository.product_attribute_read import (
    ProductAttributeReadRepositoryInterface,
)
from src.catalog.product.infrastructure.models.product_attribute import ProductAttribute


class SqlAlchemyProductAttributeReadRepository(ProductAttributeReadRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, attribute_id: int) -> Optional[ProductAttributeReadDTO]:
        stmt = select(
            ProductAttribute.id,
            ProductAttribute.name,
            ProductAttribute.is_filterable,
            ProductAttribute.is_groupable,
        ).where(ProductAttribute.id == attribute_id)

        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return None

        return ProductAttributeReadDTO(
            id=row.id,
            name=row.name,
            value="",
            is_filterable=row.is_filterable,
            is_groupable=row.is_groupable,
        )

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductAttributeReadDTO], int]:

        stmt = select(
            ProductAttribute.id,
            ProductAttribute.name,
            ProductAttribute.is_filterable,
            ProductAttribute.is_groupable,
        )

        count_stmt = select(func.count()).select_from(ProductAttribute)

        if name:
            stmt = stmt.where(ProductAttribute.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(
                ProductAttribute.name.ilike(f"%{name}%")
            )

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [
            ProductAttributeReadDTO(
                id=row.id,
                name=row.name,
                value="",
                is_filterable=row.is_filterable,
                is_groupable=row.is_groupable,
            )
            for row in result.all()
        ]
        total = count_result.scalar() or 0
        return items, total
