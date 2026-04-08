from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.regions.domain.aggregates.region import RegionAggregate
from src.regions.domain.exceptions import (
    RegionAlreadyExists,
    RegionNotFound,
)
from src.regions.domain.repository.region import RegionRepository
from src.regions.infrastructure.models.region import Region


class SqlAlchemyRegionRepository(RegionRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, region_id: int) -> Optional[RegionAggregate]:
        stmt = select(Region).where(Region.id == region_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return RegionAggregate(
            region_id=model.id,
            name=model.name,
            parent_id=model.parent_id,
        )

    async def get_list(self) -> List[RegionAggregate]:
        stmt = select(Region)
        result = await self.db.execute(stmt)

        return [
            RegionAggregate(
                region_id=m.id,
                name=m.name,
                parent_id=m.parent_id,
            )
            for m in result.scalars().all()
        ]

    async def create(self, aggregate: RegionAggregate) -> RegionAggregate:
        model = Region(
            name=aggregate.name,
            parent_id=aggregate.parent_id,
        )

        self.db.add(model)

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise RegionAlreadyExists()

        aggregate._set_id(model.id)
        return aggregate

    async def delete(self, region_id: int) -> bool:
        model = await self.db.get(Region, region_id)
        if not model:
            return False

        await self.db.delete(model)
        return True

    async def update(self, aggregate: RegionAggregate) -> RegionAggregate:
        model = await self.db.get(Region, aggregate.id)

        if not model:
            raise RegionNotFound()

        model.name = aggregate.name
        model.parent_id = aggregate.parent_id

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise RegionAlreadyExists()

        return aggregate
