from typing import Optional

from src.catalog.product.application.read_models.product_type_read_repository import (
    ProductTypeReadRepository,
)
from src.catalog.product.domain.exceptions import ProductTypeNotFound


class ProductTypeQueries:

    def __init__(self, read_repository: ProductTypeReadRepository):
        self.read_repository = read_repository

    async def get_by_id(self, product_type_id: int):
        result = await self.read_repository.get_by_id(product_type_id)
        if not result:
            raise ProductTypeNotFound()
        return result

    async def filter(self, name: Optional[str], limit: int, offset: int):
        return await self.read_repository.filter(name, limit, offset)
