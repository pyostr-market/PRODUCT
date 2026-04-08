from typing import Optional

from src.regions.domain.exceptions import RegionNotFound
from src.regions.domain.repository.region_read import (
    RegionReadRepositoryInterface,
)


class RegionQueries:
    """Query handler для чтения данных о регионах."""

    def __init__(self, read_repository: RegionReadRepositoryInterface):
        self.read_repository = read_repository

    async def get_by_id(self, region_id: int):
        """Получить регион по ID."""
        result = await self.read_repository.get_by_id(region_id)
        if not result:
            raise RegionNotFound()
        return result

    async def filter(self, name: Optional[str], parent_id: Optional[int], limit: int, offset: int):
        """Фильтрация регионов с пагинацией."""
        return await self.read_repository.filter(name, parent_id, limit, offset)

    async def get_children(self, parent_id: int):
        """Получить дочерние регионы."""
        return await self.read_repository.get_children(parent_id)
