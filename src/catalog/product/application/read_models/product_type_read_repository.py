from typing import List, Optional, Tuple

from src.catalog.product.application.dto.product_type import ProductTypeReadDTO
from src.catalog.product.domain.repository.product_type_read import (
    ProductTypeReadRepositoryInterface,
)


class ProductTypeReadRepository:
    """
    Read-модель для ProductType.
    Делегирует вызовы в инфраструктурную реализацию.
    """

    def __init__(self, repository: ProductTypeReadRepositoryInterface):
        self._repository = repository

    async def get_by_id(self, product_type_id: int) -> Optional[ProductTypeReadDTO]:
        return await self._repository.get_by_id(product_type_id)

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductTypeReadDTO], int]:
        return await self._repository.filter(
            name=name,
            limit=limit,
            offset=offset,
        )

    async def get_tree(self) -> List[ProductTypeReadDTO]:
        return await self._repository.get_tree()
