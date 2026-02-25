from typing import Optional

from src.catalog.category.application.read_models.pricing_policy_read_repository import (
    CategoryPricingPolicyReadRepository,
)
from src.catalog.category.domain.exceptions import CategoryPricingPolicyNotFound


class CategoryPricingPolicyQueries:

    def __init__(self, read_repository: CategoryPricingPolicyReadRepository):
        self.read_repository = read_repository

    async def get_by_id(self, pricing_policy_id: int):
        result = await self.read_repository.get_by_id(pricing_policy_id)
        if not result:
            raise CategoryPricingPolicyNotFound()
        return result

    async def get_by_category_id(self, category_id: int):
        result = await self.read_repository.get_by_category_id(category_id)
        if not result:
            raise CategoryPricingPolicyNotFound()
        return result

    async def filter(
        self,
        category_id: Optional[int],
        limit: int,
        offset: int,
    ):
        return await self.read_repository.filter(category_id, limit, offset)
