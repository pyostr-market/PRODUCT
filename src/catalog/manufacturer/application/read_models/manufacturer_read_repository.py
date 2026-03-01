from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.application.dto.manufacturer import ManufacturerReadDTO
from src.catalog.manufacturer.infrastructure.models.manufacturer import Manufacturer


class ManufacturerReadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, manufacturer_id: int) -> Optional[ManufacturerReadDTO]:
        stmt = select(
            Manufacturer.id,
            Manufacturer.name,
            Manufacturer.description,
        ).where(Manufacturer.id == manufacturer_id)

        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return None

        return ManufacturerReadDTO(*row)

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ManufacturerReadDTO], int]:

        stmt = select(
            Manufacturer.id,
            Manufacturer.name,
            Manufacturer.description,
        )

        count_stmt = select(func.count()).select_from(Manufacturer)

        if name:
            stmt = stmt.where(Manufacturer.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(
                Manufacturer.name.ilike(f"%{name}%")
            )

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [ManufacturerReadDTO(*row) for row in result.all()]
        total = count_result.scalar() or 0
        return items, total