from abc import ABC
from typing import Optional

from src.catalog.category.domain.aggregates.pricing_policy import (
    CategoryPricingPolicyAggregate,
)


class CategoryPricingPolicyRepository(ABC):

    async def get_by_category_id(
        self, category_id: int
    ) -> Optional[CategoryPricingPolicyAggregate]:
        ...

    async def get(self, pricing_policy_id: int) -> Optional[CategoryPricingPolicyAggregate]:
        ...

    async def create(
        self, aggregate: CategoryPricingPolicyAggregate
    ) -> CategoryPricingPolicyAggregate:
        ...

    async def delete(self, pricing_policy_id: int) -> bool:
        ...

    async def update(
        self, aggregate: CategoryPricingPolicyAggregate
    ) -> CategoryPricingPolicyAggregate:
        ...
