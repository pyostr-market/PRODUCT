from src.catalog.product.application.dto.audit import ProductTypeAuditDTO
from src.catalog.product.application.dto.product_type import (
    ProductTypeCreateDTO,
    ProductTypeReadDTO,
)
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class CreateProductTypeCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        dto: ProductTypeCreateDTO,
        user: User,
    ) -> ProductTypeReadDTO:

        async with self.uow:
            aggregate = ProductTypeAggregate(
                name=dto.name,
                parent_id=dto.parent_id,
            )

            await self.repository.create(aggregate)

            await self.audit_repository.log_product_type(
                ProductTypeAuditDTO(
                    product_type_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "parent_id": aggregate.parent_id,
                    },
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            result = ProductTypeReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                parent_id=aggregate.parent_id,
            )

        self.event_bus.publish_nowait(
            build_event(
                event_type="crud",
                method="create",
                app="products",
                entity="product_type",
                entity_id=result.id,
                data={
                    "product_type_id": result.id,
                    "fields": {
                        "name": result.name,
                        "parent_id": result.parent_id,
                    },
                },
            )
        )
        return result
