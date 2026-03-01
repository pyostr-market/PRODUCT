from typing import List, Optional, Tuple

from sqlalchemy import func, select

from src.catalog.product.infrastructure.models.product_audit_logs import ProductAuditLog


class ProductAdminQueries:

    def __init__(self, db):
        self.db = db

    async def filter_logs(
        self,
        product_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductAuditLog], int]:
        stmt = select(ProductAuditLog)
        count_stmt = select(func.count()).select_from(ProductAuditLog)

        if product_id:
            stmt = stmt.where(ProductAuditLog.product_id == product_id)
            count_stmt = count_stmt.where(ProductAuditLog.product_id == product_id)

        if user_id:
            stmt = stmt.where(ProductAuditLog.user_id == user_id)
            count_stmt = count_stmt.where(ProductAuditLog.user_id == user_id)

        if action:
            stmt = stmt.where(ProductAuditLog.action == action)
            count_stmt = count_stmt.where(ProductAuditLog.action == action)

        stmt = stmt.order_by(ProductAuditLog.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        return result.scalars().all(), count_result.scalar() or 0
