from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.domain.aggregates.pricing_policy import (
    CategoryPricingPolicyAggregate,
)
from src.catalog.category.domain.exceptions import (
    CategoryPricingPolicyAlreadyExists,
    CategoryPricingPolicyCategoryNotFound,
    CategoryPricingPolicyNotFound,
)
from src.catalog.category.domain.repository.pricing_policy import (
    CategoryPricingPolicyRepository,
)
from src.catalog.category.infrastructure.models.categories import Category
from src.catalog.category.infrastructure.models.categories_pricing import (
    CategoryPricingPolicy,
)


class SqlAlchemyCategoryPricingPolicyRepository(CategoryPricingPolicyRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_category_id(
        self, category_id: int
    ) -> Optional[CategoryPricingPolicyAggregate]:
        stmt = select(CategoryPricingPolicy).where(
            CategoryPricingPolicy.category_id == category_id
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def get(
        self, pricing_policy_id: int
    ) -> Optional[CategoryPricingPolicyAggregate]:
        stmt = select(CategoryPricingPolicy).where(
            CategoryPricingPolicy.id == pricing_policy_id
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def create(
        self, aggregate: CategoryPricingPolicyAggregate
    ) -> CategoryPricingPolicyAggregate:
        # Проверяем существование категории
        category = await self.db.get(Category, aggregate.category_id)
        if not category:
            raise CategoryPricingPolicyCategoryNotFound(
                details={"category_id": aggregate.category_id}
            )

        model = CategoryPricingPolicy(
            category_id=aggregate.category_id,
            markup_fixed=aggregate.markup_fixed,
            markup_percent=aggregate.markup_percent,
            commission_percent=aggregate.commission_percent,
            discount_percent=aggregate.discount_percent,
            tax_rate=aggregate.tax_rate,
        )

        self.db.add(model)

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise CategoryPricingPolicyAlreadyExists()

        aggregate._set_id(model.id)
        return aggregate

    async def delete(self, pricing_policy_id: int) -> bool:
        model = await self.db.get(CategoryPricingPolicy, pricing_policy_id)
        if not model:
            return False

        await self.db.delete(model)
        return True

    async def update(
        self, aggregate: CategoryPricingPolicyAggregate
    ) -> CategoryPricingPolicyAggregate:
        model = await self.db.get(CategoryPricingPolicy, aggregate.id)

        if not model:
            raise CategoryPricingPolicyNotFound()

        model.markup_fixed = aggregate.markup_fixed
        model.markup_percent = aggregate.markup_percent
        model.commission_percent = aggregate.commission_percent
        model.discount_percent = aggregate.discount_percent
        model.tax_rate = aggregate.tax_rate

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise CategoryPricingPolicyAlreadyExists()

        return aggregate

    def _to_aggregate(
        self, model: CategoryPricingPolicy
    ) -> CategoryPricingPolicyAggregate:
        return CategoryPricingPolicyAggregate(
            category_id=model.category_id,
            markup_fixed=model.markup_fixed,
            markup_percent=model.markup_percent,
            commission_percent=model.commission_percent,
            discount_percent=model.discount_percent,
            tax_rate=model.tax_rate,
            pricing_policy_id=model.id,
        )
