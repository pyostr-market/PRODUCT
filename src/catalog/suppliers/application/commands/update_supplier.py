from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.application.dto.supplier import (
    SupplierReadDTO,
    SupplierUpdateDTO,
)
from src.catalog.suppliers.domain.exceptions import SupplierNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class UpdateSupplierCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        supplier_id: int,
        dto: SupplierUpdateDTO,
        user: User,
    ) -> SupplierReadDTO:

        async with self.uow:
            aggregate = await self.repository.get(supplier_id)

            if not aggregate:
                raise SupplierNotFound()

            old_data = {
                "name": aggregate.name,
                "contact_email": aggregate.contact_email,
                "phone": aggregate.phone,
            }

            aggregate.update(dto.name, dto.contact_email, dto.phone)
            await self.repository.update(aggregate)

            new_data = {
                "name": aggregate.name,
                "contact_email": aggregate.contact_email,
                "phone": aggregate.phone,
            }

            if old_data != new_data:
                await self.audit_repository.log(
                    SupplierAuditDTO(
                        supplier_id=aggregate.id,
                        action="update",
                        old_data=old_data,
                        new_data=new_data,
                        user_id=user.id,
                    )
                )

            result = SupplierReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                contact_email=aggregate.contact_email,
                phone=aggregate.phone,
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
                    app="suppliers",
                    entity="supplier",
                    entity_id=result.id,
                    data={
                        "supplier_id": result.id,
                        "fields": changed_fields,
                    },
                )
            )
        return result
