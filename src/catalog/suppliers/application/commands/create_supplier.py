from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.application.dto.supplier import (
    SupplierCreateDTO,
    SupplierReadDTO,
)
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class CreateSupplierCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        dto: SupplierCreateDTO,
        user: User,
    ) -> SupplierReadDTO:

        async with self.uow:
            aggregate = SupplierAggregate(
                name=dto.name,
                contact_email=dto.contact_email,
                phone=dto.phone,
            )

            await self.repository.create(aggregate)

            await self.audit_repository.log(
                SupplierAuditDTO(
                    supplier_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "contact_email": aggregate.contact_email,
                        "phone": aggregate.phone,
                    },
                    user_id=user.id,
                )
            )

            result = SupplierReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                contact_email=aggregate.contact_email,
                phone=aggregate.phone,
            )

        self.event_bus.publish_nowait(
            build_event(
                event_type="crud",
                method="create",
                app="suppliers",
                entity="supplier",
                entity_id=result.id,
                data={
                    "supplier_id": result.id,
                    "fields": {
                        "name": result.name,
                        "contact_email": result.contact_email,
                        "phone": result.phone,
                    },
                },
            )
        )
        return result
