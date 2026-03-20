from src.catalog.product.application.dto.audit import ProductTypeAuditDTO
from src.catalog.product.application.dto.product_type import (
    ProductTypeImageOperationDTO,
    ProductTypeImageReadDTO,
    ProductTypeReadDTO,
    ProductTypeUpdateDTO,
)
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.domain.aggregates.product_type_image import ProductTypeImageAggregate
from src.catalog.product.domain.exceptions import ProductTypeNotFound
from src.catalog.product.domain.repository.product_type import ProductTypeRepository
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event
from src.uploads.domain.repository.upload_history import UploadHistoryRepository


class UpdateProductTypeCommand:

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
        product_type_id: int,
        dto: ProductTypeUpdateDTO,
        user: User,
    ) -> ProductTypeReadDTO:

        async with self.uow:
            aggregate = await self.repository.get(product_type_id)

            if not aggregate:
                raise ProductTypeNotFound()

            old_image_data = None
            if aggregate.image:
                old_image_data = {"upload_id": aggregate.image.upload_id}

            old_data = {
                "name": aggregate.name,
                "parent_id": aggregate.parent_id,
                "image": old_image_data,
            }

            # Применяем операцию с изображением, если передана
            if dto.image:
                await self._process_image_operation(dto.image, aggregate)

            aggregate.update(dto.name, dto.parent_id)

            await self.repository.update(aggregate)

            new_image_data = None
            if aggregate.image:
                new_image_data = {"upload_id": aggregate.image.upload_id}

            new_data = {
                "name": aggregate.name,
                "parent_id": aggregate.parent_id,
                "image": new_image_data,
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

    async def _process_image_operation(
        self,
        op: ProductTypeImageOperationDTO,
        aggregate: ProductTypeAggregate,
    ):
        """Обработать операцию с изображением."""
        if op.action == "delete":
            aggregate.remove_image()
        elif op.action in ("create", "update"):
            if op.upload_id:
                upload_record = await self.upload_history_repository.get(op.upload_id)
                if upload_record:
                    aggregate.set_image(ProductTypeImageAggregate(
                        upload_id=upload_record.upload_id,
                        object_key=upload_record.file_path,
                    ))
        # action "pass" — оставляем существующее изображение без изменений
