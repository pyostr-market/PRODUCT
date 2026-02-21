from src.catalog.product.application.dto.audit import ProductAttributeAuditDTO
from src.catalog.product.application.dto.product import ProductAttributeReadDTO
from src.catalog.product.domain.aggregates.product import ProductAttributeAggregate
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class CreateProductAttributeCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        dto: ProductAttributeAggregate,
        user: User,
    ) -> ProductAttributeReadDTO:

        async with self.uow:
            aggregate = ProductAttributeAggregate(
                name=dto.name,
                value=dto.value,
                is_filterable=dto.is_filterable,
            )

            await self.repository.create(aggregate)

            await self.audit_repository.log_product_attribute(
                ProductAttributeAuditDTO(
                    product_attribute_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "value": aggregate.value,
                        "is_filterable": aggregate.is_filterable,
                    },
                    user_id=user.id,
                )
            )

            result = ProductAttributeReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                value=aggregate.value,
                is_filterable=aggregate.is_filterable,
            )

        self.event_bus.publish_nowait(
            build_event(
                event_type="crud",
                method="create",
                app="products",
                entity="product_attribute",
                entity_id=result.id,
                data={
                    "product_attribute_id": result.id,
                    "fields": {
                        "name": result.name,
                        "value": result.value,
                        "is_filterable": result.is_filterable,
                    },
                },
            )
        )
        return result
