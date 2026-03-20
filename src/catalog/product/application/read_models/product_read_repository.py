from typing import List, Optional, Tuple

from src.catalog.product.application.dto.product import ProductReadDTO, CatalogFiltersDTO
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
        attributes: Optional[dict[str, list[str]]] = None,
        sort_type: str = "default",
        product_ids: Optional[List[int]] = None,
    ) -> Tuple[List[ProductReadDTO], int]:
        return await self._repository.filter(
            name=name,
            category_id=category_id,
            product_type_id=product_type_id,
            limit=limit,
            offset=offset,
            attributes=attributes,
            sort_type=sort_type,
            product_ids=product_ids,
        )

    async def get_catalog_filters(
        self,
        category_id: Optional[int] = None,
        device_type_id: Optional[int] = None,
    ) -> CatalogFiltersDTO:
        return await self._repository.get_catalog_filters(
            category_id=category_id,
            device_type_id=device_type_id,
        )

    async def export_full_catalog(self):
        return await self._repository.export_full_catalog()