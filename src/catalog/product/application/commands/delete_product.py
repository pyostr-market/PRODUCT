from src.catalog.product.application.dto.audit import ProductAuditDTO
from src.catalog.product.domain.exceptions import ProductNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images.storage import S3ImageStorageService


class DeleteProductCommand:

    def __init__(
        self,
        repository,
        audit_repository,
        uow,
        image_storage: S3ImageStorageService,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage
        self.event_bus = event_bus

    async def execute(self, product_id: int, user: User) -> bool:
        image_keys: list[str] = []

        async with self.uow:
            aggregate = await self.repository.get(product_id)

            if not aggregate:
                raise ProductNotFound()

            image_keys = [image.object_key for image in aggregate.images]

            old_data = {
                "name": aggregate.name,
                "description": aggregate.description,
                "price": str(aggregate.price),
                "category_id": aggregate.category_id,
                "supplier_id": aggregate.supplier_id,
                "product_type_id": aggregate.product_type_id,
                "images": [
                    {"image_key": image.object_key, "is_main": image.is_main}
                    for image in aggregate.images
                ],
                "attributes": [
                    {
                        "name": attribute.name,
                        "value": attribute.value,
                        "is_filterable": attribute.is_filterable,
                    }
                    for attribute in aggregate.attributes
                ],
            }

            await self.repository.delete(product_id)

            await self.audit_repository.log(
                ProductAuditDTO(
                    product_id=product_id,
                    action="delete",
                    old_data=old_data,
                    new_data=None,
                    user_id=user.id,
                    fio=user.fio,
                )
            )

        for key in image_keys:
            await self.image_storage.delete_object(key)

        self.event_bus.publish_many_nowait(
            [
                build_event(
                    event_type="crud",
                    method="delete",
                    app="products",
                    entity="product",
                    entity_id=product_id,
                    data={"product_id": product_id},
                ),
                build_event(
                    event_type="crud",
                    method="delete",
                    app="images",
                    entity="product_images",
                    entity_id=product_id,
                    data={"product_id": product_id},
                ),
            ]
        )

        return True
