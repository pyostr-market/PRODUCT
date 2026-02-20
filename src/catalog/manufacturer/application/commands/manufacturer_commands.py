from src.catalog.manufacturer.application.dto import (
    ManufacturerCreateDTO,
    ManufacturerReadDTO,
    ManufacturerUpdateDTO,
)
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.catalog.manufacturer.domain.exceptions import (
    ManufacturerAlreadyExists,
    ManufacturerNotFound,
)
from src.core.exceptions.service_errors import ConflictError


class ManufacturerCommands:

    def __init__(self, repository, uow):
        self.repository = repository
        self.uow = uow

    async def create(self, dto: ManufacturerCreateDTO) -> ManufacturerReadDTO:
        async with self.uow:
            aggregate = ManufacturerAggregate(
                name=dto.name,
                description=dto.description,
            )

            await self.repository.create(aggregate)

            return ManufacturerReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                description=aggregate.description,
            )

    async def update(self, manufacturer_id: int, dto: ManufacturerUpdateDTO):
        async with self.uow:
            aggregate = await self.repository.get(manufacturer_id)

            if not aggregate:
                raise ManufacturerNotFound()

            aggregate.update(dto.name, dto.description)

            await self.repository.update(aggregate)
            return aggregate

    async def delete(self, manufacturer_id: int):
        async with self.uow:
            deleted = await self.repository.delete(manufacturer_id)
            if not deleted:
                raise ManufacturerNotFound()
            return True