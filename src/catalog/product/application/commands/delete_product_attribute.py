from src.catalog.product.application.dto.audit import ProductAttributeAuditDTO
from src.catalog.product.domain.exceptions import ProductAttributeNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class DeleteProductAttributeCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        attribute_id: int,
        user: User,
    ) -> bool:

        async with self.uow:
            aggregate = await self.repository.get(attribute_id)

            if not aggregate:
                raise ProductAttributeNotFound()

            old_data = {
                "name": aggregate.name,
                "value": aggregate.value,
                "is_filterable": aggregate.is_filterable,
            }

            await self.repository.delete(attribute_id)

            await self.audit_repository.log_product_attribute(
                ProductAttributeAuditDTO(
                    product_attribute_id=attribute_id,
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
                app="products",
                entity="product_attribute",
                entity_id=attribute_id,
                data={"product_attribute_id": attribute_id},
            )
        )
        return True
