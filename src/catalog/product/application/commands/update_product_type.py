from src.catalog.product.application.dto.audit import ProductTypeAuditDTO
from src.catalog.product.application.dto.product_type import (
    ProductTypeReadDTO,
    ProductTypeUpdateDTO,
)
from src.catalog.product.domain.exceptions import ProductTypeNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class UpdateProductTypeCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        product_type_id: int,
        dto: ProductTypeUpdateDTO,
        user: User,
    ) -> ProductTypeReadDTO:

        async with self.uow:
            aggregate = await self.repository.get(product_type_id)

            if not aggregate:
                raise ProductTypeNotFound()

            old_data = {
                "name": aggregate.name,
                "parent_id": aggregate.parent_id,
            }

            aggregate.update(dto.name, dto.parent_id)

            await self.repository.update(aggregate)

            new_data = {
                "name": aggregate.name,
                "parent_id": aggregate.parent_id,
            }

            if old_data != new_data:
                await self.audit_repository.log_product_type(
                    ProductTypeAuditDTO(
                        product_type_id=aggregate.id,
                        action="update",
                        old_data=old_data,
                        new_data=new_data,
                        user_id=user.id,
                        fio=user.fio,
                    )
                )

            result = ProductTypeReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                parent_id=aggregate.parent_id,
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
                    entity="product_type",
                    entity_id=result.id,
                    data={
                        "product_type_id": result.id,
                        "fields": changed_fields,
                    },
                )
            )
        return result
