from typing import List, Optional, Tuple

from sqlalchemy import func, select

from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.domain.repository.audit import SupplierAuditRepository
from src.catalog.suppliers.infrastructure.models.supplier_audit_logs import (
    SupplierAuditLog,
)


class SqlAlchemySupplierAuditRepository(SupplierAuditRepository):
    """SQLAlchemy реализация репозитория для аудит-логов поставщиков."""

    def __init__(self, db):
        self.db = db

    async def log(self, dto: SupplierAuditDTO):
        """Записать аудит-лог."""
        model = SupplierAuditLog(
            supplier_id=dto.supplier_id,
            action=dto.action,
            old_data=dto.old_data,
            new_data=dto.new_data,
            user_id=dto.user_id,
            fio=dto.fio,
        )
        self.db.add(model)
        await self.db.flush()

    async def filter_logs(
        self,
        supplier_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[SupplierAuditLog], int]:
        """Фильтрация аудит-логов с пагинацией."""
        stmt = select(SupplierAuditLog)
        count_stmt = select(func.count()).select_from(SupplierAuditLog)

        if supplier_id:
            stmt = stmt.where(SupplierAuditLog.supplier_id == supplier_id)
            count_stmt = count_stmt.where(SupplierAuditLog.supplier_id == supplier_id)

        if user_id:
            stmt = stmt.where(SupplierAuditLog.user_id == user_id)
            count_stmt = count_stmt.where(SupplierAuditLog.user_id == user_id)

        if action:
            stmt = stmt.where(SupplierAuditLog.action == action)
            count_stmt = count_stmt.where(SupplierAuditLog.action == action)

        stmt = stmt.order_by(SupplierAuditLog.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = result.scalars().all()
        total = count_result.scalar() or 0

        return items, total
