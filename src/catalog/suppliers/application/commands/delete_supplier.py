from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.domain.exceptions import SupplierNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class DeleteSupplierCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        supplier_id: int,
        user: User,
    ) -> bool:

        async with self.uow:
            aggregate = await self.repository.get(supplier_id)

            if not aggregate:
                raise SupplierNotFound()

            old_data = {
                "name": aggregate.name,
                "contact_email": aggregate.contact_email,
                "phone": aggregate.phone,
            }

            await self.repository.delete(supplier_id)

            await self.audit_repository.log(
                SupplierAuditDTO(
                    supplier_id=supplier_id,
                    action="delete",
                    old_data=old_data,
                    new_data=None,
                    user_id=user.id,
                )
            )

        self.event_bus.publish_nowait(
            build_event(
                event_type="crud",
                method="delete",
                app="suppliers",
                entity="supplier",
                entity_id=supplier_id,
                data={"supplier_id": supplier_id},
            )
        )
        return True
