from typing import List, Optional, Tuple

from src.catalog.product.application.dto.product_type import ProductTypeReadDTO
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

    async def tree(self) -> Tuple[List[ProductTypeReadDTO], int]:
        """
        Получить все типы продуктов в виде дерева.
        Возвращает список корневых типов с вложенными детьми.
        """
        all_types = await self.read_repository.get_tree()

        # Создаём словарь для быстрого доступа по ID
        types_by_id = {t.id: t for t in all_types}

        # Распределяем типы по родителям
        root_types = []
        for t in all_types:
            t.children = []

        for t in all_types:
            if t.parent_id is None:
                root_types.append(t)
            else:
                parent = types_by_id.get(t.parent_id)
                if parent:
                    parent.children.append(t)

        return root_types, len(all_types)
