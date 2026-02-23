from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.catalog.product.application.dto.audit import ProductAuditDTO
from src.catalog.product.application.dto.product import (
    ProductAttributeReadDTO,
    ProductImageReadDTO,
    ProductReadDTO,
)
from src.catalog.product.domain.aggregates.product import (
    ProductAttributeAggregate,
    ProductImageAggregate,
)
from src.catalog.product.domain.exceptions import ProductNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images.storage import S3ImageStorageService
from src.uploads.infrastructure.models.upload_history import UploadHistory


class UpdateProductCommand:

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

    async def execute(self, product_id: int, dto, user: User) -> ProductReadDTO:
        try:
            async with self.uow:
                aggregate = await self.repository.get(product_id)

                if not aggregate:
                    raise ProductNotFound()

                old_data = {
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

                aggregate.update(
                    name=dto.name,
                    description=dto.description,
                    price=dto.price,
                    category_id=dto.category_id,
                    supplier_id=dto.supplier_id,
                    product_type_id=dto.product_type_id,
                )

                if dto.images is not None:
                    final_images: list[ProductImageAggregate] = []

                    for op in dto.images:
                        if op.action == "delete":
                            # Удаляем по upload_id
                            if op.upload_id is not None:
                                for img in aggregate.images:
                                    if img.upload_id == op.upload_id:
                                        break

                        elif op.action == "pass":
                            # Сохраняем по upload_id
                            if op.upload_id is not None:
                                for img in aggregate.images:
                                    if img.upload_id == op.upload_id:
                                        final_images.append(
                                            ProductImageAggregate(
                                                upload_id=img.upload_id,
                                                is_main=op.is_main if op.is_main is not None else img.is_main,
                                                ordering=op.ordering if op.ordering is not None else img.ordering,
                                                object_key=img.object_key,
                                            )
                                        )
                                        break

                        elif op.action == "create":
                            if op.upload_id is not None:
                                # Проверяем, что upload_id существует
                                stmt = select(UploadHistory).where(UploadHistory.id == op.upload_id)
                                result = await self.db.execute(stmt)
                                upload_record = result.scalar_one_or_none()

                                if upload_record:
                                    final_images.append(
                                        ProductImageAggregate(
                                            upload_id=upload_record.id,
                                            is_main=op.is_main if op.is_main is not None else False,
                                            ordering=op.ordering if op.ordering is not None else 0,
                                            object_key=upload_record.file_path,
                                        )
                                    )

                    # Нормализуем is_main
                    if final_images and not any(img.is_main for img in final_images):
                        final_images[0].is_main = True

                    aggregate.replace_images(final_images)

                if dto.attributes is not None:
                    aggregate.replace_attributes(
                        [
                            ProductAttributeAggregate(
                                name=attribute.name,
                                value=attribute.value,
                                is_filterable=attribute.is_filterable,
                            )
                            for attribute in dto.attributes
                        ]
                    )

                await self.repository.update(aggregate)

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

                if old_data != new_data:
                    await self.audit_repository.log(
                        ProductAuditDTO(
                            product_id=aggregate.id,
                            action="update",
                            old_data=old_data,
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
                    app="products",
                    entity="product",
                    entity_id=result.id,
                    data={
                        "product_id": result.id,
                        "fields": changed_fields,
                    },
                )
            ]
            if "price" in changed_fields:
                events.append(
                    build_event(
                        event_type="field_update",
                        method="price_update",
                        app="products",
                        entity="product",
                        entity_id=result.id,
                        data={
                            "product_id": result.id,
                            "price": {
                                "old": old_data.get("price"),
                                "new": changed_fields["price"],
                            },
                        },
                    )
                )
            if "product_type_id" in changed_fields:
                events.append(
                    build_event(
                        event_type="field_update",
                        method="update",
                        app="device_types",
                        entity="product_type",
                        entity_id=result.id,
                        data={
                            "product_id": result.id,
                            "product_type_id": {
                                "old": old_data.get("product_type_id"),
                                "new": changed_fields["product_type_id"],
                            },
                        },
                    )
                )
            if "images" in changed_fields:
                events.append(
                    build_event(
                        event_type="field_update",
                        method="update",
                        app="images",
                        entity="product_images",
                        entity_id=result.id,
                        data={
                            "product_id": result.id,
                            "images": changed_fields["images"],
                        },
                    )
                )
            self.event_bus.publish_many_nowait(events)

        return result
