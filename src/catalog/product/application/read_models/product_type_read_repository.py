from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.product.application.dto.product_type import ProductTypeReadDTO
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.infrastructure.models.product_type import ProductType


class ProductTypeReadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_read_dto(self, model: ProductType) -> ProductTypeReadDTO:
        parent_dto = None
        if model.parent:
            parent_dto = ProductTypeAggregate(
                product_type_id=model.parent.id,
                name=model.parent.name,
                parent_id=model.parent.parent_id,
                parent=None,
            )
        return ProductTypeReadDTO(
            id=model.id,
            name=model.name,
            parent=parent_dto,
        )

    async def get_by_id(self, product_type_id: int) -> Optional[ProductTypeReadDTO]:
        stmt = select(ProductType).options(
            selectinload(ProductType.parent)
        ).where(ProductType.id == product_type_id)

        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductTypeReadDTO], int]:

        stmt = select(ProductType).options(
            selectinload(ProductType.parent)
        )

        count_stmt = select(func.count()).select_from(ProductType)

        if name:
            stmt = stmt.where(ProductType.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(
                ProductType.name.ilike(f"%{name}%")
            )

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [self._to_read_dto(model) for model in result.scalars().all()]
        total = count_result.scalar() or 0
        return items, total
