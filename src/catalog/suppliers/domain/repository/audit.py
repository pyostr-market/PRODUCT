from abc import ABC
from typing import List, Optional, Tuple

from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.infrastructure.models.supplier_audit_logs import (
    SupplierAuditLog,
)


class SupplierAuditRepository(ABC):
    """Интерфейс репозитория для аудит-логов поставщиков."""

    async def log(self, dto: SupplierAuditDTO):
        """Записать аудит-лог."""
        raise NotImplementedError

    async def filter_logs(
        self,
        supplier_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[SupplierAuditLog], int]:
        """Фильтрация аудит-логов с пагинацией."""
        raise NotImplementedError
