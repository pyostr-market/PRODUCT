from src.catalog.product.application.dto.audit import ProductTypeAuditDTO
from src.catalog.product.domain.exceptions import ProductTypeNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class DeleteProductTypeCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        product_type_id: int,
        user: User,
    ) -> bool:

        async with self.uow:
            aggregate = await self.repository.get(product_type_id)

            if not aggregate:
                raise ProductTypeNotFound()

            old_data = {
                "name": aggregate.name,
                "parent_id": aggregate.parent_id,
            }

            await self.repository.delete(product_type_id)

            await self.audit_repository.log_product_type(
                ProductTypeAuditDTO(
                    product_type_id=product_type_id,
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
                entity="product_type",
                entity_id=product_type_id,
                data={"product_type_id": product_type_id},
            )
        )
        return True
