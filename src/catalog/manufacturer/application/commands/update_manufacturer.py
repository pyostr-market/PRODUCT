from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.application.dto.manufacturer import (
    ManufacturerReadDTO,
    ManufacturerUpdateDTO,
)
from src.catalog.manufacturer.domain.exceptions import ManufacturerNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class UpdateManufacturerCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

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

            result = ManufacturerReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                description=aggregate.description,
            )

        changed_fields = {
            key: value
            for key, value in new_data.items()
            if old_data.get(key) != value
        }
        if changed_fields:
            self.event_bus.publish_nowait(
                build_event(
                    event_type="crud",
                    method="update",
                    app="manufacturers",
                    entity="manufacturer",
                    entity_id=result.id,
                    data={
                        "manufacturer_id": result.id,
                        "fields": changed_fields,
                    },
                )
            )
        return result
