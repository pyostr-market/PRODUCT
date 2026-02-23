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
from src.core.services.images.storage import S3ImageStorageService
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
            if not image.upload_id:
                from src.catalog.product.domain.exceptions import ProductInvalidImage
                raise ProductInvalidImage(details={"reason": "upload_id_required"})

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
                            image_key="",
                            image_url="",
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
