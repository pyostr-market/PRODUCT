from typing import List, Optional, Tuple

from src.catalog.product.domain.repository.product_type_audit_query import (
    ProductTypeAuditQueryRepository,
)
from src.catalog.product.infrastructure.models.product_audit_logs import (
    ProductTypeAuditLog,
)


class ProductTypeAdminQueries:
    """
    Query-сервис для админских запросов к логам аудита типов продуктов.
    Делегирует вызовы в инфраструктурную реализацию.
    """

    def __init__(self, repository: ProductTypeAuditQueryRepository):
        self._repository = repository

    async def filter_logs(
        self,
        product_type_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductTypeAuditLog], int]:
        return await self._repository.filter_logs(
            product_type_id=product_type_id,
            user_id=user_id,
            action=action,
            limit=limit,
            offset=offset,
        )
