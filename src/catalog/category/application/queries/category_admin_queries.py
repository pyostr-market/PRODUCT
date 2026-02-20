from typing import List, Optional, Tuple

from sqlalchemy import func, select

from src.catalog.category.infrastructure.models.category_audit_logs import CategoryAuditLog


class CategoryAdminQueries:

    def __init__(self, db):
        self.db = db

    async def filter_logs(
        self,
        category_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[CategoryAuditLog], int]:

        stmt = select(CategoryAuditLog)
        count_stmt = select(func.count()).select_from(CategoryAuditLog)

        if category_id:
            stmt = stmt.where(CategoryAuditLog.category_id == category_id)
            count_stmt = count_stmt.where(CategoryAuditLog.category_id == category_id)

        if user_id:
            stmt = stmt.where(CategoryAuditLog.user_id == user_id)
            count_stmt = count_stmt.where(CategoryAuditLog.user_id == user_id)

        if action:
            stmt = stmt.where(CategoryAuditLog.action == action)
            count_stmt = count_stmt.where(CategoryAuditLog.action == action)

        stmt = stmt.order_by(CategoryAuditLog.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = result.scalars().all()
        total = count_result.scalar() or 0

        return items, total
