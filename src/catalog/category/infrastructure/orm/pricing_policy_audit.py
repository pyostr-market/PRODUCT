from src.catalog.category.application.dto.pricing_policy_audit import (
    CategoryPricingPolicyAuditDTO,
)
from src.catalog.category.infrastructure.models.pricing_policy_audit_logs import (
    CategoryPricingPolicyAuditLog,
)


class SqlAlchemyCategoryPricingPolicyAuditRepository:

    def __init__(self, db):
        self.db = db

    async def log(self, dto: CategoryPricingPolicyAuditDTO):
        model = CategoryPricingPolicyAuditLog(
            pricing_policy_id=dto.pricing_policy_id,
            action=dto.action,
            old_data=dto.old_data,
            new_data=dto.new_data,
            user_id=dto.user_id,
            fio=dto.fio,
        )
        self.db.add(model)
        await self.db.flush()
