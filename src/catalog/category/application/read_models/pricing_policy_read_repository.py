from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.category.application.dto.pricing_policy import (
    CategoryPricingPolicyReadDTO,
)
from src.catalog.category.infrastructure.models.categories_pricing import (
    CategoryPricingPolicy,
)


class CategoryPricingPolicyReadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_read_dto(self, model: CategoryPricingPolicy) -> CategoryPricingPolicyReadDTO:
        return CategoryPricingPolicyReadDTO(
            id=model.id,
            category_id=model.category_id,
            markup_fixed=model.markup_fixed,
            markup_percent=model.markup_percent,
            commission_percent=model.commission_percent,
            discount_percent=model.discount_percent,
            tax_rate=model.tax_rate,
        )

    async def get_by_id(self, pricing_policy_id: int) -> Optional[CategoryPricingPolicyReadDTO]:
        stmt = select(CategoryPricingPolicy).where(
            CategoryPricingPolicy.id == pricing_policy_id
        )

        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        return self._to_read_dto(model)

    async def get_by_category_id(
        self, category_id: int
    ) -> Optional[CategoryPricingPolicyReadDTO]:
        stmt = select(CategoryPricingPolicy).where(
            CategoryPricingPolicy.category_id == category_id
        )

        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        return self._to_read_dto(model)

    async def filter(
        self,
        category_id: Optional[int],
        limit: int,
        offset: int,
    ) -> Tuple[List[CategoryPricingPolicyReadDTO], int]:

        stmt = select(CategoryPricingPolicy)
        count_stmt = select(func.count()).select_from(CategoryPricingPolicy)

        if category_id is not None:
            stmt = stmt.where(CategoryPricingPolicy.category_id == category_id)
            count_stmt = count_stmt.where(CategoryPricingPolicy.category_id == category_id)

        stmt = stmt.order_by(CategoryPricingPolicy.id).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [self._to_read_dto(model) for model in result.scalars().all()]
        total = count_result.scalar() or 0
        return items, total
