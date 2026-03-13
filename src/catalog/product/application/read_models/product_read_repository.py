from typing import List, Optional, Tuple

from src.catalog.product.application.dto.product import ProductReadDTO
from src.catalog.product.domain.repository.product_read import (
    ProductReadRepositoryInterface,
)


class ProductReadRepository:
    """
    Read-модель для Product.
    Делегирует вызовы в инфраструктурную реализацию.
    """

    def __init__(self, repository: ProductReadRepositoryInterface):
        self._repository = repository

    async def get_by_id(self, product_id: int) -> Optional[ProductReadDTO]:
        return await self._repository.get_by_id(product_id)

    async def get_by_name(self, name: str) -> Optional[ProductReadDTO]:
        return await self._repository.get_by_name(name)

    async def filter(
        self,
        name: Optional[str],
        category_id: Optional[int],
        product_type_id: Optional[int],
        limit: int,
        offset: int,
        attributes: Optional[dict[str, str]] = None,
    ) -> Tuple[List[ProductReadDTO], int]:
        return await self._repository.filter(
            name=name,
            category_id=category_id,
            product_type_id=product_type_id,
            limit=limit,
            offset=offset,
            attributes=attributes,
        )

    async def export_full_catalog(self):
        return await self._repository.export_full_catalog()