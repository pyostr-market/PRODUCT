from abc import ABC
from typing import List, Optional, Tuple

from src.catalog.suppliers.application.dto.supplier import SupplierReadDTO


class SupplierReadRepositoryInterface(ABC):
    """Интерфейс репозитория для чтения поставщиков."""

    async def get_by_id(self, supplier_id: int) -> Optional[SupplierReadDTO]:
        """Получить поставщика по ID."""
        raise NotImplementedError

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[SupplierReadDTO], int]:
        """Фильтрация поставщиков с пагинацией."""
        raise NotImplementedError
