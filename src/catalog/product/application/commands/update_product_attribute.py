from src.catalog.product.application.dto.audit import ProductAttributeAuditDTO
from src.catalog.product.application.dto.product import ProductAttributeReadDTO
from src.catalog.product.domain.aggregates.product import ProductAttributeAggregate
from src.catalog.product.domain.exceptions import ProductAttributeNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class UpdateProductAttributeCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        attribute_id: int,
        dto: ProductAttributeAggregate,
        user: User,
    ) -> ProductAttributeReadDTO:

        async with self.uow:
            aggregate = await self.repository.get(attribute_id)

            if not aggregate:
                raise ProductAttributeNotFound()

            old_data = {
                "name": aggregate.name,
                "value": aggregate.value,
                "is_filterable": aggregate.is_filterable,
            }

            aggregate.update(
                name=dto.name,
                value=dto.value,
                is_filterable=dto.is_filterable,
            )

            await self.repository.update(aggregate)

            new_data = {
                "name": aggregate.name,
                "value": aggregate.value,
                "is_filterable": aggregate.is_filterable,
            }

            if old_data != new_data:
                await self.audit_repository.log_product_attribute(
                    ProductAttributeAuditDTO(
                        product_attribute_id=aggregate.id,
                        action="update",
                        old_data=old_data,
                        new_data=new_data,
                        user_id=user.id,
                    )
                )

            result = ProductAttributeReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                value=aggregate.value,
                is_filterable=aggregate.is_filterable,
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
                    app="products",
                    entity="product_attribute",
                    entity_id=result.id,
                    data={
                        "product_attribute_id": result.id,
                        "fields": changed_fields,
                    },
                )
            )
        return result
