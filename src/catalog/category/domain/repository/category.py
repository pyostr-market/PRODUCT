from abc import ABC
from typing import Optional

from src.catalog.category.domain.aggregates.category import CategoryAggregate


class CategoryRepository(ABC):

    async def get(self, category_id: int) -> Optional[CategoryAggregate]:
        ...

    async def create(self, aggregate: CategoryAggregate) -> CategoryAggregate:
        ...

    async def delete(self, category_id: int) -> bool:
        ...

    async def update(self, aggregate: CategoryAggregate) -> CategoryAggregate:
        ...
