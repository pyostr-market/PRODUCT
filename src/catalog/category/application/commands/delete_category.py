from src.catalog.category.application.dto.audit import CategoryAuditDTO
from src.catalog.category.domain.exceptions import CategoryNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images import ImageStorageService


class DeleteCategoryCommand:

    def __init__(
        self,
        repository,
        audit_repository,
        uow,
        image_storage: ImageStorageService,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage
        self.event_bus = event_bus

    async def execute(
        self,
        category_id: int,
        user: User,
    ) -> bool:

        image_keys: list[str] = []

        async with self.uow:
            aggregate = await self.repository.get(category_id)

            if not aggregate:
                raise CategoryNotFound()

            image_keys = [image.object_key for image in aggregate.images]

            old_data = {
                "name": aggregate.name,
                "description": aggregate.description,
                "parent_id": aggregate.parent_id,
                "manufacturer_id": aggregate.manufacturer_id,
                "images": [
                    {"image_key": image.object_key, "ordering": image.ordering}
                    for image in aggregate.images
                ],
            }

            await self.repository.delete(category_id)

            await self.audit_repository.log(
                CategoryAuditDTO(
                    category_id=category_id,
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
                    app="categories",
                    entity="category",
                    entity_id=category_id,
                    data={"category_id": category_id},
                ),
                build_event(
                    event_type="crud",
                    method="delete",
                    app="images",
                    entity="category_images",
                    entity_id=category_id,
                    data={"category_id": category_id},
                ),
            ]
        )

        return True
