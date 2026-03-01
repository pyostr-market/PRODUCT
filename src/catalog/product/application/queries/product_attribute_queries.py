from typing import Optional

from src.catalog.product.application.read_models.product_attribute_read_repository import (
    ProductAttributeReadRepository,
)


class ProductAttributeQueries:

    def __init__(self, read_repository: ProductAttributeReadRepository):
        self.read_repository = read_repository

    async def get_by_id(self, attribute_id: int):
        return await self.read_repository.get_by_id(attribute_id)

    async def filter(self, name: Optional[str], limit: int, offset: int):
        return await self.read_repository.filter(name, limit, offset)
