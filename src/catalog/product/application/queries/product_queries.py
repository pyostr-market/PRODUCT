from typing import Optional

from src.catalog.product.application.dto.product import ProductReadDTO
from src.catalog.product.application.read_models.product_read_repository import (
    ProductReadRepository,
)
from src.catalog.product.domain.exceptions import ProductNotFound, ProductRelatedLookupRequired
from src.catalog.product.domain.repository.product import ProductRepository
from src.core.services.images import ImageStorageService


class ProductQueries:

    def __init__(
        self,
        read_repository: ProductReadRepository,
        repository: ProductRepository,
        image_storage: ImageStorageService,
    ):
        self.read_repository = read_repository
        self.repository = repository
        self.image_storage = image_storage

    def _attach_image_url(self, dto: ProductReadDTO) -> ProductReadDTO:
        for image in dto.images:
            image.image_url = self.image_storage.build_public_url(image.image_key)
        return dto

    async def get_by_id(self, product_id: int) -> ProductReadDTO:
        dto = await self.read_repository.get_by_id(product_id)
        if not dto:
            raise ProductNotFound()
        return self._attach_image_url(dto)

    async def filter(
        self,
        name: Optional[str],
        category_id: Optional[int],
        product_type_id: Optional[int],
        limit: int,
        offset: int,
    ):
        items, total = await self.read_repository.filter(
            name=name,
            category_id=category_id,
            product_type_id=product_type_id,
            limit=limit,
            offset=offset,
        )
        return [self._attach_image_url(item) for item in items], total

    async def related(
        self,
        product_id: Optional[int],
        name: Optional[str],
    ):
        if product_id is None and not name:
            raise ProductRelatedLookupRequired()

        aggregate = None

        if product_id is not None:
            aggregate = await self.repository.get(product_id)

        if aggregate is None and name:
            aggregate = await self.repository.get_by_name(name)

        if aggregate is None:
            raise ProductNotFound()

        related_aggregates = await self.repository.get_related_by_filterable_attributes(
            product_id=aggregate.id,
            category_id=aggregate.category_id,
        )

        items = []
        for related in related_aggregates:
            dto = await self.read_repository.get_by_id(related.id)
            if dto:
                items.append(self._attach_image_url(dto))

        return items
