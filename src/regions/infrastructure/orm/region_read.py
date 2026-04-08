from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.regions.application.dto.region import RegionReadDTO
from src.regions.domain.repository.region_read import (
    RegionReadRepositoryInterface,
)
from src.regions.infrastructure.models.region import Region


class SqlAlchemyRegionReadRepository(RegionReadRepositoryInterface):
    """SQLAlchemy реализация репозитория для чтения регионов."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, region_id: int) -> Optional[RegionReadDTO]:
        stmt = select(
            Region.id,
            Region.name,
            Region.parent_id,
        ).where(Region.id == region_id)

        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return None

        return RegionReadDTO(*row)

    async def filter(
        self,
        name: Optional[str],
        parent_id: Optional[int],
        limit: int,
        offset: int,
    ) -> Tuple[List[RegionReadDTO], int]:

        stmt = select(
            Region.id,
            Region.name,
            Region.parent_id,
        )

        count_stmt = select(func.count()).select_from(Region)

        if name:
            stmt = stmt.where(Region.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(Region.name.ilike(f"%{name}%"))

        if parent_id is not None:
            stmt = stmt.where(Region.parent_id == parent_id)
            count_stmt = count_stmt.where(Region.parent_id == parent_id)

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [RegionReadDTO(*row) for row in result.all()]
        total = count_result.scalar() or 0
        return items, total

    async def get_children(self, parent_id: int) -> List[RegionReadDTO]:
        """Получить дочерние регионы."""
        stmt = select(
            Region.id,
            Region.name,
            Region.parent_id,
        ).where(Region.parent_id == parent_id)

        result = await self.db.execute(stmt)
        return [RegionReadDTO(*row) for row in result.all()]
