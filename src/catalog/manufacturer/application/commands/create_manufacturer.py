from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.application.dto.manufacturer import (
    ManufacturerCreateDTO,
    ManufacturerReadDTO,
)
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.core.auth.schemas.user import User


class CreateManufacturerCommand:

    def __init__(self, repository, audit_repository, uow):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow

    async def execute(
        self,
        dto: ManufacturerCreateDTO,
        user: User,
    ) -> ManufacturerReadDTO:

        async with self.uow:
            aggregate = ManufacturerAggregate(
                name=dto.name,
                description=dto.description,
            )

            await self.repository.create(aggregate)

            await self.audit_repository.log(
                ManufacturerAuditDTO(
                    manufacturer_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "description": aggregate.description,
                    },
                    user_id=user.id,
                )
            )

            return ManufacturerReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                description=aggregate.description,
            )