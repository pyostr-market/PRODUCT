from src.catalog.category.application.dto.audit import CategoryAuditDTO
from src.catalog.category.application.dto.category import (
    CategoryImageOperationDTO,
    CategoryImageReadDTO,
    CategoryReadDTO,
    CategoryUpdateDTO,
)
from src.catalog.category.domain.aggregates.category import (
    CategoryAggregate,
    CategoryImageAggregate,
)
from src.catalog.category.domain.exceptions import CategoryNotFound
from src.catalog.category.infrastructure.services.related_data_loader import (
    CategoryRelatedDataLoader,
)
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images import ImageStorageService


class UpdateCategoryCommand:

    def __init__(
        self,
        repository,
        audit_repository,
        uow,
        image_storage: ImageStorageService,
        event_bus: AsyncEventBus,
        data_loader: CategoryRelatedDataLoader,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage
        self.event_bus = event_bus
        self.data_loader = data_loader

    async def execute(
        self,
        category_id: int,
        dto: CategoryUpdateDTO,
        user: User,
    ) -> CategoryReadDTO:

        old_image_key: str | None = None
        new_image_key: str | None = None

        try:
            async with self.uow:
                aggregate = await self.repository.get(category_id)

                if not aggregate:
                    raise CategoryNotFound()

                old_image_key = aggregate.image.object_key if aggregate.image else None
                old_data = {
                    "name": aggregate.name,
                    "description": aggregate.description,
                    "parent_id": aggregate.parent_id,
                    "manufacturer_id": aggregate.manufacturer_id,
                    "image": {"upload_id": aggregate.image.upload_id} if aggregate.image else None,
                }

                aggregate.update(
                    dto.name,
                    dto.description,
                    dto.parent_id,
                    dto.manufacturer_id,
                )

                if dto.image is not None:
                    # Обрабатываем операцию с изображением
                    op = dto.image
                    
                    if op.action == "delete":
                        # Удаляем изображение
                        aggregate.remove_image()
                    elif op.action == "create":
                        # Добавляем новое изображение
                        if op.upload_id:
                            upload_id, object_key = await self.data_loader.get_upload_info(op.upload_id)
                            new_image_key = object_key
                            aggregate.set_image(CategoryImageAggregate(
                                upload_id=upload_id,
                                object_key=object_key,
                            ))
                    elif op.action == "update":
                        # Обновляем существующее изображение
                        if op.upload_id:
                            upload_id, object_key = await self.data_loader.get_upload_info(op.upload_id)
                            new_image_key = object_key
                            aggregate.set_image(CategoryImageAggregate(
                                upload_id=upload_id,
                                object_key=object_key,
                            ))
                    elif op.action == "pass":
                        # Сохраняем существующее изображение без изменений
                        pass

                await self.repository.update(aggregate)

                new_image_data = {"upload_id": aggregate.image.upload_id} if aggregate.image else None
                new_data = {
                    "name": aggregate.name,
                    "description": aggregate.description,
                    "parent_id": aggregate.parent_id,
                    "manufacturer_id": aggregate.manufacturer_id,
                    "image": new_image_data,
                }

                if old_data != new_data:
                    await self.audit_repository.log(
                        CategoryAuditDTO(
                            category_id=aggregate.id,
                            action="update",
                            old_data=old_data,
                            new_data=new_data,
                            user_id=user.id,
                            fio=user.fio,
                        )
                    )

                # Загружаем данные для parent и manufacturer через сервис
                parent_dto = None
                if aggregate.parent_id:
                    parent_dto = await self.data_loader.get_parent_category(aggregate.parent_id)

                manufacturer_dto = None
                if aggregate.manufacturer_id:
                    manufacturer_dto = await self.data_loader.get_manufacturer(aggregate.manufacturer_id)

                result_image = None
                if aggregate.image:
                    result_image = CategoryImageReadDTO(
                        upload_id=aggregate.image.upload_id,
                        image_key=aggregate.image.object_key or "",
                        image_url=self.image_storage.build_public_url(aggregate.image.object_key) if aggregate.image.object_key else "",
                    )

                result = CategoryReadDTO(
                    id=aggregate.id,
                    name=aggregate.name,
                    description=aggregate.description,
                    image=result_image,
                    parent=parent_dto,
                    manufacturer=manufacturer_dto,
                )
        except Exception:
            raise

        if new_image_key and old_image_key and old_image_key != new_image_key:
            await self.image_storage.delete_object(old_image_key)

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
            if "image" in changed_fields:
                events.append(
                    build_event(
                        event_type="field_update",
                        method="update",
                        app="images",
                        entity="category_images",
                        entity_id=result.id,
                        data={
                            "category_id": result.id,
                            "image": changed_fields["image"],
                        },
                    )
                )
            self.event_bus.publish_many_nowait(events)

        return result
