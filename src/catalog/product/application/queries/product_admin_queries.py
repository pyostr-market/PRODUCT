from typing import List, Optional, Tuple

from src.catalog.product.domain.repository.product_audit_query import (
    ProductAuditQueryRepository,
)
from src.catalog.product.infrastructure.models.product_audit_logs import ProductAuditLog


class ProductAdminQueries:
    """
    Query-сервис для админских запросов к логам аудита продуктов.
    Делегирует вызовы в инфраструктурную реализацию.
    """

    def __init__(self, repository: ProductAuditQueryRepository):
        self._repository = repository

    async def filter_logs(
        self,
        product_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductAuditLog], int]:
        return await self._repository.filter_logs(
            product_id=product_id,
            user_id=user_id,
            action=action,
            limit=limit,
            offset=offset,
        )
