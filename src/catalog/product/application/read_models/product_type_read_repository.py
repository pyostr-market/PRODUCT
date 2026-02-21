from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.application.dto.product_type import ProductTypeReadDTO
from src.catalog.product.infrastructure.models.product_type import ProductType


class ProductTypeReadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, product_type_id: int) -> Optional[ProductTypeReadDTO]:
        stmt = select(
            ProductType.id,
            ProductType.name,
            ProductType.parent_id,
        ).where(ProductType.id == product_type_id)

        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return None

        return ProductTypeReadDTO(*row)

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductTypeReadDTO], int]:

        stmt = select(
            ProductType.id,
            ProductType.name,
            ProductType.parent_id,
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

        items = [ProductTypeReadDTO(*row) for row in result.all()]
        total = count_result.scalar() or 0
        return items, total
