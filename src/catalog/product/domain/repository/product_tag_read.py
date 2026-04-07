from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from src.catalog.product.application.dto.product import ProductTagReadDTO


class ProductTagReadRepositoryInterface(ABC):
    """Интерфейс read-репозитория для получения связей товаров с тегами."""

    @abstractmethod
    async def get_by_product(
        self,
        product_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[ProductTagReadDTO], int]:
        """Получить все связи для товара с информацией о тегах."""
        pass
