from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.catalog.product.application.dto.audit import ProductAuditDTO
from src.catalog.product.application.dto.product import (
    ProductAttributeReadDTO,
    ProductImageReadDTO,
    ProductReadDTO,
)
from src.catalog.product.domain.aggregates.product import (
    ProductAggregate,
    ProductAttributeAggregate,
    ProductImageAggregate,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images.storage import S3ImageStorageService, guess_content_type
from src.uploads.infrastructure.models.upload_history import UploadHistory


class CreateProductCommand:

    def __init__(
        self,
        repository,
        audit_repository,
        uow,
        image_storage: S3ImageStorageService,
        event_bus: AsyncEventBus,
        db: AsyncSession,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage
        self.event_bus = event_bus
        self.db = db

    async def execute(self, dto, user: User) -> ProductReadDTO:
        mapped_images: list[ProductImageAggregate] = []
        
        for image in dto.images:
            if image.upload_id:
                # Используем предварительно загруженное изображение из UploadHistory
                stmt = select(UploadHistory).where(UploadHistory.id == image.upload_id)
                result = await self.db.execute(stmt)
                upload_record = result.scalar_one_or_none()
                
                if not upload_record:
                    from src.catalog.product.domain.exceptions import ProductInvalidImage
                    raise ProductInvalidImage(details={"reason": "upload_not_found", "upload_id": image.upload_id})
                
                mapped_images.append(
                    ProductImageAggregate(
                        upload_id=upload_record.id,
                        is_main=image.is_main,
                        ordering=image.ordering,
                        object_key=upload_record.file_path,
                    )
                )
            elif image.image:
                # Загружаем изображение напрямую и создаём запись в UploadHistory
                image_key = self.image_storage.build_key(folder="products", filename=image.image_name)
                content_type = guess_content_type(image.image_name)
                await self.image_storage.upload_bytes(data=image.image, key=image_key, content_type=content_type)

                # Создаём запись в UploadHistory
                upload_record = UploadHistory(
                    user_id=None,  # Будет установлено позже или через context
                    file_path=image_key,
                    folder="products",
                    content_type=content_type,
                    original_filename=image.image_name,
                    file_size=len(image.image),
                )
                self.db.add(upload_record)
                await self.db.flush()

                mapped_images.append(
                    ProductImageAggregate(
                        upload_id=upload_record.id,
                        is_main=image.is_main,
                        ordering=image.ordering,
                        object_key=image_key,
                    )
                )

        mapped_attributes = [
            ProductAttributeAggregate(
                name=attribute.name,
                value=attribute.value,
                is_filterable=attribute.is_filterable,
            )
            for attribute in dto.attributes
        ]

        try:
            async with self.uow:
                aggregate = ProductAggregate(
                    name=dto.name,
                    description=dto.description,
                    price=dto.price,
                    category_id=dto.category_id,
                    supplier_id=dto.supplier_id,
                    product_type_id=dto.product_type_id,
                    images=mapped_images,
                    attributes=mapped_attributes,
                )

                await self.repository.create(aggregate)

                new_data = {
                    "name": aggregate.name,
                    "description": aggregate.description,
                    "price": str(aggregate.price),
                    "category_id": aggregate.category_id,
                    "supplier_id": aggregate.supplier_id,
                    "product_type_id": aggregate.product_type_id,
                    "images": [
                        {"upload_id": image.upload_id, "is_main": image.is_main}
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

                await self.audit_repository.log(
                    ProductAuditDTO(
                        product_id=aggregate.id,
                        action="create",
                        old_data=None,
                        new_data=new_data,
                        user_id=user.id,
                        fio=user.fio,
                    )
                )

                result = ProductReadDTO(
                    id=aggregate.id,
                    name=aggregate.name,
                    description=aggregate.description,
                    price=aggregate.price,
                    category_id=aggregate.category_id,
                    supplier_id=aggregate.supplier_id,
                    product_type_id=aggregate.product_type_id,
                    images=[
                        ProductImageReadDTO(
                            image_id=image.upload_id,
                            image_key="",  # Будет заполнено из UploadHistory
                            image_url="",  # Будет заполнено из UploadHistory
                            is_main=image.is_main,
                            ordering=image.ordering,
                            upload_id=image.upload_id,
                        )
                        for image in aggregate.images
                    ],
                    attributes=[
                        ProductAttributeReadDTO(
                            name=attribute.name,
                            value=attribute.value,
                            is_filterable=attribute.is_filterable,
                        )
                        for attribute in aggregate.attributes
                    ],
                )
        except Exception:
            raise

        self.event_bus.publish_many_nowait(
            [
                build_event(
                    event_type="crud",
                    method="create",
                    app="products",
                    entity="product",
                    entity_id=result.id,
                    data={
                        "product_id": result.id,
                        "fields": {
                            "name": result.name,
                            "description": result.description,
                            "price": str(result.price),
                            "category_id": result.category_id,
                            "supplier_id": result.supplier_id,
                            "product_type_id": result.product_type_id,
                        },
                    },
                ),
                build_event(
                    event_type="crud",
                    method="create",
                    app="images",
                    entity="product_images",
                    entity_id=result.id,
                    data={
                        "product_id": result.id,
                        "images": [
                            {"upload_id": image.upload_id, "is_main": image.is_main}
                            for image in result.images
                        ],
                    },
                ),
            ]
        )
        return result
