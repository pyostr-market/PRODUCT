from abc import ABC
from typing import List, Optional, Tuple

from src.catalog.product.infrastructure.models.product_audit_logs import (
    ProductTypeAuditLog,
)


class ProductTypeAuditQueryRepository(ABC):

    async def filter_logs(
        self,
        product_type_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductTypeAuditLog], int]:
        """Фильтрация логов аудита типов продуктов."""
        raise NotImplementedError
