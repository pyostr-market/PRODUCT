from typing import List, Optional, Tuple

from src.catalog.product.application.dto.product_attribute import ProductAttributeReadDTO
from src.catalog.product.domain.repository.product_attribute_read import ProductAttributeReadRepositoryInterface


class ProductAttributeReadRepository:
    """
    Read-модель для ProductAttribute.
    Делегирует вызовы в инфраструктурную реализацию.
    """

    def __init__(self, repository: ProductAttributeReadRepositoryInterface):
        self._repository = repository

    async def get_by_id(self, attribute_id: int) -> Optional[ProductAttributeReadDTO]:
        return await self._repository.get_by_id(attribute_id)

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductAttributeReadDTO], int]:
        return await self._repository.filter(
            name=name,
            limit=limit,
            offset=offset,
        )
