from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.infrastructure.models.manufacturer_audit_logs import (
    ManufacturerAuditLog,
)


class SqlAlchemyManufacturerAuditQueries:
    """
    Infrastructure реализация для запросов аудита.
    
    Работает напрямую с ORM моделями и SQLAlchemy.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def filter_logs(
        self,
        manufacturer_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ManufacturerAuditLog], int]:
        """
        Фильтрация логов аудита.
        
        Возвращает список записей и общее количество.
        """
        stmt = select(ManufacturerAuditLog)
        count_stmt = select(func.count()).select_from(ManufacturerAuditLog)

        if manufacturer_id:
            stmt = stmt.where(ManufacturerAuditLog.manufacturer_id == manufacturer_id)
            count_stmt = count_stmt.where(
                ManufacturerAuditLog.manufacturer_id == manufacturer_id
            )

        if user_id:
            stmt = stmt.where(ManufacturerAuditLog.user_id == user_id)
            count_stmt = count_stmt.where(ManufacturerAuditLog.user_id == user_id)

        if action:
            stmt = stmt.where(ManufacturerAuditLog.action == action)
            count_stmt = count_stmt.where(ManufacturerAuditLog.action == action)

        stmt = stmt.order_by(ManufacturerAuditLog.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = result.scalars().all()
        total = count_result.scalar() or 0

        return items, total
