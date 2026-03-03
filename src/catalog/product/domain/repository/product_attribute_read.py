from abc import ABC
from typing import List, Optional, Tuple

from src.catalog.product.application.dto.product_attribute import ProductAttributeReadDTO


class ProductAttributeReadRepositoryInterface(ABC):

    async def get_by_id(self, attribute_id: int) -> Optional[ProductAttributeReadDTO]:
        """Получить атрибут по ID."""
        raise NotImplementedError

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ProductAttributeReadDTO], int]:
        """Фильтрация атрибутов с пагинацией."""
        raise NotImplementedError
