from abc import ABC
from typing import List, Optional, Tuple

from src.catalog.product.infrastructure.models.product_audit_logs import ProductAuditLog


class ProductAuditQueryRepository(ABC):

    async def filter_logs(
        self,
        product_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductAuditLog], int]:
        """Фильтрация логов аудита продуктов."""
        raise NotImplementedError
