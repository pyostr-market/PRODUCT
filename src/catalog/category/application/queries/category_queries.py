from typing import Optional

from src.catalog.category.application.read_models.category_read_repository import CategoryReadRepository
from src.catalog.category.domain.exceptions import CategoryNotFound
from src.core.services.images import ImageStorageService


class CategoryQueries:

    def __init__(
        self,
        read_repository: CategoryReadRepository,
        image_storage: ImageStorageService,
    ):
        self.read_repository = read_repository
        self.image_storage = image_storage

    def _attach_image_url(self, dto):
        dto.images = sorted(dto.images, key=lambda i: i.ordering)
        for image in dto.images:
            image.image_url = self.image_storage.build_public_url(image.image_key)
        return dto

    async def get_by_id(self, category_id: int):
        result = await self.read_repository.get_by_id(category_id)
        if not result:
            raise CategoryNotFound()
        return self._attach_image_url(result)

    async def filter(self, name: Optional[str], limit: int, offset: int):
        items, total = await self.read_repository.filter(name, limit, offset)
        return [self._attach_image_url(i) for i in items], total
