from abc import ABC
from typing import List, Optional, Tuple

from src.catalog.product.application.dto.product_type import ProductTypeReadDTO


class ProductTypeReadRepositoryInterface(ABC):

    async def get_by_id(self, product_type_id: int) -> Optional[ProductTypeReadDTO]:
        """Получить тип продукта по ID."""
        raise NotImplementedError

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductTypeReadDTO], int]:
        """Фильтрация типов продуктов с пагинацией."""
        raise NotImplementedError
