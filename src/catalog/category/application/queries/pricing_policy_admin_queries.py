from typing import List, Optional, Tuple

from sqlalchemy import func, select

from src.catalog.category.infrastructure.models.pricing_policy_audit_logs import (
    CategoryPricingPolicyAuditLog,
)


class CategoryPricingPolicyAdminQueries:

    def __init__(self, db):
        self.db = db

    async def filter_logs(
        self,
        pricing_policy_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[CategoryPricingPolicyAuditLog], int]:

        stmt = select(CategoryPricingPolicyAuditLog)
        count_stmt = select(func.count()).select_from(CategoryPricingPolicyAuditLog)

        if pricing_policy_id:
            stmt = stmt.where(CategoryPricingPolicyAuditLog.pricing_policy_id == pricing_policy_id)
            count_stmt = count_stmt.where(CategoryPricingPolicyAuditLog.pricing_policy_id == pricing_policy_id)

        if user_id:
            stmt = stmt.where(CategoryPricingPolicyAuditLog.user_id == user_id)
            count_stmt = count_stmt.where(CategoryPricingPolicyAuditLog.user_id == user_id)

        if action:
            stmt = stmt.where(CategoryPricingPolicyAuditLog.action == action)
            count_stmt = count_stmt.where(CategoryPricingPolicyAuditLog.action == action)

        stmt = stmt.order_by(CategoryPricingPolicyAuditLog.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = result.scalars().all()
        total = count_result.scalar() or 0

        return items, total
