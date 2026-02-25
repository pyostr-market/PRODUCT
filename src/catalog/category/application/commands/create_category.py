from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images import ImageStorageService
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
            # Используем предварительно загруженное изображение
            stmt = select(UploadHistory).where(UploadHistory.id == image.upload_id)
            result = await self.db.execute(stmt)
            upload_record = result.scalar_one_or_none()

            if not upload_record:
                from src.catalog.category.domain.exceptions import (
                    CategoryInvalidImage,
                )
                raise CategoryInvalidImage(details={"reason": "upload_not_found", "upload_id": image.upload_id})

            uploaded_images.append(CategoryImageAggregate(
                upload_id=upload_record.id,
                ordering=image.ordering,
                object_key=upload_record.file_path,
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
                            ordering=image.ordering,
                            image_key="",  # Будет заполнено из UploadHistory
                            image_url="",  # Будет заполнено из UploadHistory
                            upload_id=image.upload_id,
                        )
                        for image in sorted(aggregate.images, key=lambda i: i.ordering)
                    ],
                    parent=parent_dto,
                    manufacturer=manufacturer_dto,
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
                            "parent_id": parent_dto.id if parent_dto else None,
                            "manufacturer_id": manufacturer_dto.id if manufacturer_dto else None,
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
