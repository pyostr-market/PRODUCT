from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.catalog.manufacturer.domain.exceptions import (
    ManufacturerAlreadyExists,
    ManufacturerNotFound,
)
from src.catalog.manufacturer.domain.repository.manufacturer import ManufacturerRepository
from src.catalog.manufacturer.infrastructure.models.manufacturer import Manufacturer


class SqlAlchemyManufacturerRepository(ManufacturerRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, manufacturer_id: int) -> Optional[ManufacturerAggregate]:
        stmt = select(Manufacturer).where(
            Manufacturer.id == manufacturer_id
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return ManufacturerAggregate(
            manufacturer_id=model.id,
            name=model.name,
            description=model.description,
        )

    async def get_list(self) -> List[ManufacturerAggregate]:
        stmt = select(Manufacturer)
        result = await self.db.execute(stmt)

        return [
            ManufacturerAggregate(
                manufacturer_id=m.id,
                name=m.name,
                description=m.description,
            )
            for m in result.scalars().all()
        ]

    async def create(self, aggregate: ManufacturerAggregate) -> ManufacturerAggregate:
        model = Manufacturer(
            name=aggregate.name,
            description=aggregate.description,
        )

        self.db.add(model)

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ManufacturerAlreadyExists()

        aggregate._set_id(model.id)
        return aggregate

    async def delete(self, manufacturer_id: int) -> bool:
        model = await self.db.get(Manufacturer, manufacturer_id)
        if not model:
            return False

        await self.db.delete(model)
        return True

    async def update(self, aggregate: ManufacturerAggregate) -> ManufacturerAggregate:
        model = await self.db.get(Manufacturer, aggregate.id)

        if not model:
            raise ManufacturerNotFound()

        model.name = aggregate.name
        model.description = aggregate.description
        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise ManufacturerAlreadyExists()

        return aggregate