from typing import Any

from src.catalog.product.application.dto.audit import ProductTypeAuditDTO
from src.catalog.product.application.dto.product_type import (
    ProductTypeCreateDTO,
    ProductTypeImageReadDTO,
    ProductTypeReadDTO,
)
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.domain.aggregates.product_type_image import ProductTypeImageAggregate
from src.catalog.product.domain.repository.product_type import ProductTypeRepository
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event
from src.uploads.domain.repository.upload_history import UploadHistoryRepository


class CreateProductTypeCommand:

    def __init__(
        self,
        repository: ProductTypeRepository,
        audit_repository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
        upload_history_repository: UploadHistoryRepository,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus
        self.upload_history_repository = upload_history_repository
        self._image_storage = None

    @property
    def image_storage(self):
        if self._image_storage is None:
            from src.core.services.images.storage import S3ImageStorageService
            self._image_storage = S3ImageStorageService.from_settings()
        return self._image_storage

    def _build_image_url(self, file_path: str) -> str:
        """Построить публичный URL для изображения."""
        try:
            return self.image_storage.build_public_url(file_path)
        except Exception:
            return ""

    async def execute(
        self,
        dto: ProductTypeCreateDTO,
        user: User,
    ) -> ProductTypeReadDTO:

        image_aggregate = None
        if dto.image and dto.image.upload_id:
            upload_record = await self.upload_history_repository.get(dto.image.upload_id)
            if upload_record:
                image_aggregate = ProductTypeImageAggregate(
                    upload_id=upload_record.upload_id,
                    object_key=upload_record.file_path,
                )

        async with self.uow:
            aggregate = ProductTypeAggregate(
                name=dto.name,
                parent_id=dto.parent_id,
            )
            
            # Устанавливаем изображение после создания агрегата
            if image_aggregate:
                aggregate.set_image(image_aggregate)

            await self.repository.create(aggregate)

            image_data = None
            if aggregate.image:
                image_data = {
                    "upload_id": aggregate.image.upload_id,
                }

            await self.audit_repository.log_product_type(
                ProductTypeAuditDTO(
                    product_type_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "parent_id": aggregate.parent_id,
                        "image": image_data,
                    },
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            # Загружаем данные для parent
            parent_dto = None
            if aggregate.parent_id:
                parent_model = await self.repository.get(aggregate.parent_id)
                if parent_model:
                    parent_dto = ProductTypeAggregate(
                        product_type_id=parent_model.id,
                        name=parent_model.name,
                        parent_id=parent_model.parent_id,
                    )

            result_image = None
            if aggregate.image:
                result_image = ProductTypeImageReadDTO(
                    upload_id=aggregate.image.upload_id,
                    image_url=self._build_image_url(aggregate.image.object_key),
                )

            result = ProductTypeReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                parent=parent_dto,
                image=result_image,
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
                        "parent_id": parent_dto.id if parent_dto else None,
                    },
                },
            )
        )
        return result
