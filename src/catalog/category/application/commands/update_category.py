from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images import ImageStorageService
from src.uploads.infrastructure.models.upload_history import UploadHistory


class UpdateCategoryCommand:

    def __init__(
        self,
        repository,
        audit_repository,
        uow,
        image_storage: ImageStorageService,
        event_bus: AsyncEventBus,
        db: AsyncSession,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage
        self.event_bus = event_bus
        self.db = db

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
                    # Обрабатываем операции с изображениями
                    final_images: list[CategoryImageAggregate] = list(aggregate.images)
                    
                    for op in dto.images:
                        if op.action == "delete":
                            # Удаляем изображение из списка
                            if op.upload_id:
                                final_images = [
                                    img for img in final_images 
                                    if img.upload_id != op.upload_id
                                ]
                        elif op.action == "create":
                            # Добавляем новое изображение
                            if op.upload_id:
                                stmt = select(UploadHistory).where(UploadHistory.id == op.upload_id)
                                result = await self.db.execute(stmt)
                                upload_record = result.scalar_one_or_none()
                                
                                if not upload_record:
                                    from src.catalog.category.domain.exceptions import CategoryInvalidImage
                                    raise CategoryInvalidImage(
                                        details={"reason": "upload_not_found", "upload_id": op.upload_id}
                                    )
                                
                                final_images.append(CategoryImageAggregate(
                                    upload_id=upload_record.id,
                                    object_key=upload_record.file_path,
                                    ordering=op.ordering or len(final_images),
                                ))
                                new_image_keys.append(upload_record.file_path)
                        elif op.action == "update":
                            # Обновляем существующее изображение
                            if op.upload_id:
                                for img in final_images:
                                    if img.upload_id == op.upload_id:
                                        if op.ordering is not None:
                                            img.ordering = op.ordering
                                        break
                        elif op.action == "pass":
                            # Сохраняем изображение, возможно обновляем ordering
                            if op.upload_id:
                                for img in final_images:
                                    if img.upload_id == op.upload_id:
                                        if op.ordering is not None:
                                            img.ordering = op.ordering
                                        break
                    
                    aggregate.replace_images(final_images)

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
                            fio=user.fio,
                        )
                    )

                # Загружаем данные для parent и manufacturer
                parent_dto = None
                if aggregate.parent_id:
                    parent_agg = await self.repository.get(aggregate.parent_id)
                    if parent_agg:
                        parent_dto = CategoryAggregate(
                            category_id=parent_agg.id,
                            name=parent_agg.name,
                            description=parent_agg.description,
                            parent_id=parent_agg.parent_id,
                            manufacturer_id=parent_agg.manufacturer_id,
                        )

                manufacturer_dto = None
                if aggregate.manufacturer_id:
                    from src.catalog.manufacturer.infrastructure.models.manufacturer import (
                        Manufacturer,
                    )
                    stmt = select(Manufacturer).where(Manufacturer.id == aggregate.manufacturer_id)
                    result = await self.db.execute(stmt)
                    manufacturer_model = result.scalar_one_or_none()
                    if manufacturer_model:
                        manufacturer_dto = ManufacturerAggregate(
                            manufacturer_id=manufacturer_model.id,
                            name=manufacturer_model.name,
                            description=manufacturer_model.description,
                        )

                result = CategoryReadDTO(
                    id=aggregate.id,
                    name=aggregate.name,
                    description=aggregate.description,
                    images=[
                        CategoryImageReadDTO(
                            upload_id=image.upload_id,
                            ordering=image.ordering,
                            image_key=image.object_key,
                            image_url=self.image_storage.build_public_url(image.object_key),
                        )
                        for image in sorted(aggregate.images, key=lambda i: i.ordering)
                    ],
                    parent=parent_dto,
                    manufacturer=manufacturer_dto,
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
