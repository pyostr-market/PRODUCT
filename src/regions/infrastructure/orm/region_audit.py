from typing import List, Optional, Tuple

from sqlalchemy import func, select

from src.regions.application.dto.audit import RegionAuditDTO
from src.regions.domain.repository.audit import RegionAuditRepository
from src.regions.infrastructure.models.region_audit_logs import (
    RegionAuditLog,
)


class SqlAlchemyRegionAuditRepository(RegionAuditRepository):
    """SQLAlchemy реализация репозитория для аудит-логов регионов."""

    def __init__(self, db):
        self.db = db

    async def log(self, dto: RegionAuditDTO):
        """Записать аудит-лог."""
        model = RegionAuditLog(
            region_id=dto.region_id,
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
        region_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[RegionAuditLog], int]:
        """Фильтрация аудит-логов с пагинацией."""
        stmt = select(RegionAuditLog)
        count_stmt = select(func.count()).select_from(RegionAuditLog)

        if region_id:
            stmt = stmt.where(RegionAuditLog.region_id == region_id)
            count_stmt = count_stmt.where(RegionAuditLog.region_id == region_id)

        if user_id:
            stmt = stmt.where(RegionAuditLog.user_id == user_id)
            count_stmt = count_stmt.where(RegionAuditLog.user_id == user_id)

        if action:
            stmt = stmt.where(RegionAuditLog.action == action)
            count_stmt = count_stmt.where(RegionAuditLog.action == action)

        stmt = stmt.order_by(RegionAuditLog.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = result.scalars().all()
        total = count_result.scalar() or 0

        return items, total
