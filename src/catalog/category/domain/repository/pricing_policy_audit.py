from abc import ABC

from src.catalog.category.application.dto.pricing_policy_audit import (
    CategoryPricingPolicyAuditDTO,
)


class CategoryPricingPolicyAuditRepository(ABC):

    async def log(self, dto: CategoryPricingPolicyAuditDTO):
        ...
