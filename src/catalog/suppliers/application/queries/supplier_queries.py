from typing import Optional

from src.catalog.suppliers.application.read_models.supplier_read_repository import (
    SupplierReadRepository,
)
from src.catalog.suppliers.domain.exceptions import SupplierNotFound


class SupplierQueries:

    def __init__(self, read_repository: SupplierReadRepository):
        self.read_repository = read_repository

    async def get_by_id(self, supplier_id: int):
        result = await self.read_repository.get_by_id(supplier_id)
        if not result:
            raise SupplierNotFound()
        return result

    async def filter(self, name: Optional[str], limit: int, offset: int):
        return await self.read_repository.filter(name, limit, offset)