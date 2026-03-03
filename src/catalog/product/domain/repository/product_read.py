from abc import ABC
from typing import List, Optional, Tuple

from src.catalog.product.application.dto.product import ProductReadDTO


class ProductReadRepositoryInterface(ABC):

    async def get_by_id(self, product_id: int) -> Optional[ProductReadDTO]:
        """Получить товар по ID."""
        raise NotImplementedError

    async def get_by_name(self, name: str) -> Optional[ProductReadDTO]:
        """Получить товар по названию."""
        raise NotImplementedError

    async def filter(
        self,
        name: Optional[str],
        category_id: Optional[int],
        product_type_id: Optional[int],
        limit: int,
        offset: int,
        attributes: Optional[dict[str, str]] = None,
    ) -> Tuple[List[ProductReadDTO], int]:
        """Фильтрация товаров с пагинацией."""
        raise NotImplementedError

    async def export_full_catalog(self):
        """Полная выгрузка каталога."""
        raise NotImplementedError