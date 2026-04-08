from abc import ABC
from typing import List, Optional, Tuple

from src.regions.application.dto.region import RegionReadDTO


class RegionReadRepositoryInterface(ABC):
    """Интерфейс репозитория для чтения регионов."""

    async def get_by_id(self, region_id: int) -> Optional[RegionReadDTO]:
        """Получить регион по ID."""
        raise NotImplementedError

    async def filter(
        self,
        name: Optional[str],
        parent_id: Optional[int],
        limit: int,
        offset: int,
    ) -> Tuple[List[RegionReadDTO], int]:
        """Фильтрация регионов с пагинацией."""
        raise NotImplementedError

    async def get_children(self, parent_id: int) -> List[RegionReadDTO]:
        """Получить дочерние регионы."""
        raise NotImplementedError
