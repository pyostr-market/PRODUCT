from typing import Optional

from src.catalog.suppliers.domain.repository.supplier_read import SupplierReadRepositoryInterface
from src.catalog.suppliers.domain.exceptions import SupplierNotFound


class SupplierQueries:
    """Query handler для чтения данных о поставщиках."""

    def __init__(self, read_repository: SupplierReadRepositoryInterface):
        self.read_repository = read_repository

    async def get_by_id(self, supplier_id: int):
        """Получить поставщика по ID."""
        result = await self.read_repository.get_by_id(supplier_id)
        if not result:
            raise SupplierNotFound()
        return result

    async def filter(self, name: Optional[str], limit: int, offset: int):
        """Фильтрация поставщиков с пагинацией."""
        return await self.read_repository.filter(name, limit, offset)
