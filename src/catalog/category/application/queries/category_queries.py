from typing import List, Optional, Tuple

from src.catalog.category.application.dto.category import CategoryReadDTO
from src.catalog.category.domain.exceptions import CategoryNotFound
from src.catalog.category.infrastructure.services.read_repository import (
    CategoryReadRepository,
)
from src.core.services.images import ImageStorageService


class CategoryQueries:

    def __init__(
        self,
        read_repository: CategoryReadRepository,
        image_storage: ImageStorageService,
    ):
        self.read_repository = read_repository
        self.image_storage = image_storage

    def _attach_image_url(self, dto):
        if dto.image:
            dto.image.image_url = self.image_storage.build_public_url(dto.image.image_key)
        return dto

    async def get_by_id(self, category_id: int):
        result = await self.read_repository.get_by_id(category_id)
        if not result:
            raise CategoryNotFound()
        return self._attach_image_url(result)

    async def filter(self, name: Optional[str], limit: int, offset: int):
        items, total = await self.read_repository.filter(name, limit, offset)
        return [self._attach_image_url(i) for i in items], total

    async def tree(self) -> Tuple[List[CategoryReadDTO], int]:
        """
        Получить все категории в виде дерева.
        Возвращает список корневых категорий с вложенными детьми.
        """
        all_categories = await self.read_repository.get_tree()

        # Создаём словарь для быстрого доступа по ID
        categories_by_id = {cat.id: cat for cat in all_categories}

        # Добавляем children к каждой категории
        for cat in all_categories:
            cat.children = []

        # Распределяем категории по родителям
        root_categories = []
        for cat in all_categories:
            if cat.parent_id is None:
                root_categories.append(cat)
            else:
                parent = categories_by_id.get(cat.parent_id)
                if parent:
                    parent.children.append(cat)

        # Применяем image_url ко всем категориям
        for cat in all_categories:
            self._attach_image_url(cat)

        return root_categories, len(all_categories)
