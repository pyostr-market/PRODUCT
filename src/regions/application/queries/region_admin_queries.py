from typing import Optional

from src.regions.domain.repository.audit import RegionAuditRepository


class RegionAdminQueries:
    """Query handler для администрирования регионов."""

    def __init__(self, audit_repository: RegionAuditRepository):
        self.audit_repository = audit_repository

    async def filter_logs(
        self,
        region_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ):
        """Фильтрация аудит-логов с пагинацией."""
        return await self.audit_repository.filter_logs(
            region_id=region_id,
            user_id=user_id,
            action=action,
            limit=limit,
            offset=offset,
        )
