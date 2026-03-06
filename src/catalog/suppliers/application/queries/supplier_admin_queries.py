from typing import List, Optional, Tuple

from src.catalog.suppliers.domain.repository.audit import SupplierAuditRepository


class SupplierAdminQueries:
    """Query handler для админских запросов к аудит-логам поставщиков."""

    def __init__(self, audit_repository: SupplierAuditRepository):
        self.audit_repository = audit_repository

    async def filter_logs(
        self,
        supplier_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ):
        """Фильтрация аудит-логов с пагинацией."""
        return await self.audit_repository.filter_logs(
            supplier_id=supplier_id,
            user_id=user_id,
            action=action,
            limit=limit,
            offset=offset,
        )
