from typing import List, Optional, Tuple

from sqlalchemy import func, select

from src.catalog.product.infrastructure.models.product_audit_logs import (
    ProductTypeAuditLog,
)


class ProductTypeAdminQueries:

    def __init__(self, db):
        self.db = db

    async def filter_logs(
        self,
        product_type_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductTypeAuditLog], int]:

        stmt = select(ProductTypeAuditLog)
        count_stmt = select(func.count()).select_from(ProductTypeAuditLog)

        if product_type_id:
            stmt = stmt.where(
                ProductTypeAuditLog.product_type_id == product_type_id
            )
            count_stmt = count_stmt.where(
                ProductTypeAuditLog.product_type_id == product_type_id
            )

        if user_id:
            stmt = stmt.where(ProductTypeAuditLog.user_id == user_id)
            count_stmt = count_stmt.where(ProductTypeAuditLog.user_id == user_id)

        if action:
            stmt = stmt.where(ProductTypeAuditLog.action == action)
            count_stmt = count_stmt.where(ProductTypeAuditLog.action == action)

        stmt = stmt.order_by(ProductTypeAuditLog.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = result.scalars().all()
        total = count_result.scalar() or 0

        return items, total
