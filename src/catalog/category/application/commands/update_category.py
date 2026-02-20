from src.catalog.category.application.dto.audit import CategoryAuditDTO
from src.catalog.category.application.dto.category import (
    CategoryImageReadDTO,
    CategoryReadDTO,
    CategoryUpdateDTO,
)
from src.catalog.category.domain.aggregates.category import CategoryImageAggregate
from src.catalog.category.domain.exceptions import CategoryNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images import ImageStorageService
from src.core.services.images.storage import guess_content_type


class UpdateCategoryCommand:

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
        dto: CategoryUpdateDTO,
        user: User,
    ) -> CategoryReadDTO:

        old_image_keys: list[str] = []
        new_image_keys: list[str] = []

        try:
            async with self.uow:
                aggregate = await self.repository.get(category_id)

                if not aggregate:
                    raise CategoryNotFound()

                old_image_keys = [image.object_key for image in aggregate.images]
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

                aggregate.update(
                    dto.name,
                    dto.description,
                    dto.parent_id,
                    dto.manufacturer_id,
                )

                if dto.images is not None:
                    uploaded_images: list[CategoryImageAggregate] = []
                    for image in dto.images:
                        new_image_key = self.image_storage.build_key(folder="categories", filename=image.image_name)
                        content_type = guess_content_type(image.image_name)
                        await self.image_storage.upload_bytes(
                            data=image.image,
                            key=new_image_key,
                            content_type=content_type,
                        )
                        new_image_keys.append(new_image_key)
                        uploaded_images.append(
                            CategoryImageAggregate(object_key=new_image_key, ordering=image.ordering)
                        )
                    aggregate.replace_images(uploaded_images)

                await self.repository.update(aggregate)

                new_data = {
                    "name": aggregate.name,
                    "description": aggregate.description,
                    "parent_id": aggregate.parent_id,
                    "manufacturer_id": aggregate.manufacturer_id,
                    "images": [
                        {"image_key": image.object_key, "ordering": image.ordering}
                        for image in aggregate.images
                    ],
                }

                if old_data != new_data:
                    await self.audit_repository.log(
                        CategoryAuditDTO(
                            category_id=aggregate.id,
                            action="update",
                            old_data=old_data,
                            new_data=new_data,
                            user_id=user.id,
                        )
                    )

                result = CategoryReadDTO(
                    id=aggregate.id,
                    name=aggregate.name,
                    description=aggregate.description,
                    parent_id=aggregate.parent_id,
                    manufacturer_id=aggregate.manufacturer_id,
                    images=[
                        CategoryImageReadDTO(
                            ordering=image.ordering,
                            image_key=image.object_key,
                            image_url=self.image_storage.build_public_url(image.object_key),
                        )
                        for image in sorted(aggregate.images, key=lambda i: i.ordering)
                    ],
                )
        except Exception:
            for key in new_image_keys:
                await self.image_storage.delete_object(key)
            raise

        if dto.images is not None:
            new_keys_set = set(new_image_keys)
            for key in old_image_keys:
                if key not in new_keys_set:
                    await self.image_storage.delete_object(key)

        changed_fields = {
            key: value
            for key, value in new_data.items()
            if old_data.get(key) != value
        }
        if changed_fields:
            events = [
                build_event(
                    event_type="crud",
                    method="update",
                    app="categories",
                    entity="category",
                    entity_id=result.id,
                    data={
                        "category_id": result.id,
                        "fields": changed_fields,
                    },
                )
            ]
            if "images" in changed_fields:
                events.append(
                    build_event(
                        event_type="field_update",
                        method="update",
                        app="images",
                        entity="category_images",
                        entity_id=result.id,
                        data={
                            "category_id": result.id,
                            "images": changed_fields["images"],
                        },
                    )
                )
            self.event_bus.publish_many_nowait(events)

        return result
