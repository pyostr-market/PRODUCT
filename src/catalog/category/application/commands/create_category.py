from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.catalog.category.application.dto.audit import CategoryAuditDTO
from src.catalog.category.application.dto.category import (
    CategoryCreateDTO,
    CategoryImageReadDTO,
    CategoryReadDTO,
)
from src.catalog.category.domain.aggregates.category import (
    CategoryAggregate,
    CategoryImageAggregate,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images import ImageStorageService
from src.core.services.images.storage import guess_content_type
from src.uploads.infrastructure.models.upload_history import UploadHistory


class CreateCategoryCommand:

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
        dto: CategoryCreateDTO,
        user: User,
    ) -> CategoryReadDTO:
        uploaded_images: list[CategoryImageAggregate] = []

        for image in dto.images:
            if image.upload_id:
                # Используем предварительно загруженное изображение
                stmt = select(UploadHistory).where(UploadHistory.id == image.upload_id)
                result = await self.db.execute(stmt)
                upload_record = result.scalar_one_or_none()
                
                if not upload_record:
                    from src.catalog.category.domain.exceptions import CategoryInvalidImage
                    raise CategoryInvalidImage(details={"reason": "upload_not_found", "upload_id": image.upload_id})
                
                uploaded_images.append(CategoryImageAggregate(
                    upload_id=upload_record.id,
                    ordering=image.ordering,
                    object_key=upload_record.file_path,
                ))
            elif image.image:
                # Загружаем изображение напрямую
                image_key = self.image_storage.build_key(folder="categories", filename=image.image_name)
                content_type = guess_content_type(image.image_name)
                await self.image_storage.upload_bytes(data=image.image, key=image_key, content_type=content_type)

                # Создаём запись в UploadHistory
                upload_record = UploadHistory(
                    user_id=None,
                    file_path=image_key,
                    folder="categories",
                    content_type=content_type,
                    original_filename=image.image_name,
                    file_size=len(image.image),
                )
                self.db.add(upload_record)
                await self.db.flush()

                uploaded_images.append(CategoryImageAggregate(
                    upload_id=upload_record.id,
                    ordering=image.ordering,
                    object_key=image_key,
                ))

        try:
            async with self.uow:
                aggregate = CategoryAggregate(
                    name=dto.name,
                    description=dto.description,
                    parent_id=dto.parent_id,
                    manufacturer_id=dto.manufacturer_id,
                    images=uploaded_images,
                )

                await self.repository.create(aggregate)

                await self.audit_repository.log(
                    CategoryAuditDTO(
                        category_id=aggregate.id,
                        action="create",
                        old_data=None,
                        new_data={
                            "name": aggregate.name,
                            "description": aggregate.description,
                            "parent_id": aggregate.parent_id,
                            "manufacturer_id": aggregate.manufacturer_id,
                            "images": [
                                {"upload_id": image.upload_id, "ordering": image.ordering}
                                for image in aggregate.images
                            ],
                        },
                        user_id=user.id,
                        fio=user.fio,
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
                            image_key="",  # Будет заполнено из UploadHistory
                            image_url="",  # Будет заполнено из UploadHistory
                            upload_id=image.upload_id,
                        )
                        for image in sorted(aggregate.images, key=lambda i: i.ordering)
                    ],
                )
        except Exception:
            raise

        self.event_bus.publish_many_nowait(
            [
                build_event(
                    event_type="crud",
                    method="create",
                    app="categories",
                    entity="category",
                    entity_id=result.id,
                    data={
                        "category_id": result.id,
                        "fields": {
                            "name": result.name,
                            "description": result.description,
                            "parent_id": result.parent_id,
                            "manufacturer_id": result.manufacturer_id,
                        },
                    },
                ),
                build_event(
                    event_type="crud",
                    method="create",
                    app="images",
                    entity="category_images",
                    entity_id=result.id,
                    data={
                        "category_id": result.id,
                        "images": [
                            {"image_key": image.image_key, "ordering": image.ordering}
                            for image in result.images
                        ],
                    },
                ),
            ]
        )
        return result
