from abc import ABC
from typing import List, Optional, Tuple

from src.regions.application.dto.audit import RegionAuditDTO
from src.regions.infrastructure.models.region_audit_logs import (
    RegionAuditLog,
)


class RegionAuditRepository(ABC):
    """Интерфейс репозитория для аудит-логов регионов."""

    async def log(self, dto: RegionAuditDTO):
        """Записать аудит-лог."""
        raise NotImplementedError

    async def filter_logs(
        self,
        region_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[RegionAuditLog], int]:
        """Фильтрация аудит-логов с пагинацией."""
        raise NotImplementedError
