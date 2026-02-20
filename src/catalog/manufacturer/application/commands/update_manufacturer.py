from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.application.dto.manufacturer import (
    ManufacturerReadDTO,
    ManufacturerUpdateDTO,
)
from src.catalog.manufacturer.domain.exceptions import ManufacturerNotFound
from src.core.auth.schemas.user import User


class UpdateManufacturerCommand:

    def __init__(self, repository, audit_repository, uow):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow

    async def execute(
        self,
        manufacturer_id: int,
        dto: ManufacturerUpdateDTO,
        user: User,
    ) -> ManufacturerReadDTO:

        async with self.uow:
            aggregate = await self.repository.get(manufacturer_id)

            if not aggregate:
                raise ManufacturerNotFound()

            old_data = {
                "name": aggregate.name,
                "description": aggregate.description,
            }

            aggregate.update(dto.name, dto.description)

            await self.repository.update(aggregate)

            new_data = {
                "name": aggregate.name,
                "description": aggregate.description,
            }

            if old_data != new_data:
                await self.audit_repository.log(
                    ManufacturerAuditDTO(
                        manufacturer_id=aggregate.id,
                        action="update",
                        old_data=old_data,
                        new_data=new_data,
                        user_id=user.id,
                    )
                )

            return ManufacturerReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                description=aggregate.description,
            )