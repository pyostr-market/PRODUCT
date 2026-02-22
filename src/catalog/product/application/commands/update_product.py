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
from src.core.services.images import ImageStorageService
from src.core.services.images.storage import guess_content_type


class UpdateProductCommand:

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

    async def execute(self, product_id: int, dto, user: User) -> ProductReadDTO:
        old_image_keys: list[str] = []
        new_image_keys: list[str] = []
        deleted_image_keys: list[str] = []

        try:
            async with self.uow:
                aggregate = await self.repository.get(product_id)

                if not aggregate:
                    raise ProductNotFound()

                old_image_keys = [image.object_key for image in aggregate.images]
                old_image_ids = {image.image_id for image in aggregate.images if image.image_id}

                old_data = {
                    "name": aggregate.name,
                    "description": aggregate.description,
                    "price": str(aggregate.price),
                    "category_id": aggregate.category_id,
                    "supplier_id": aggregate.supplier_id,
                    "product_type_id": aggregate.product_type_id,
                    "images": [
                        {"image_key": image.object_key, "is_main": image.is_main, "image_id": image.image_id}
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
                        if op.action == "to_delete":
                            # Удаляем по image_id
                            if op.image_id is not None and op.image_id in old_image_ids:
                                for img in aggregate.images:
                                    if img.image_id == op.image_id:
                                        deleted_image_keys.append(img.object_key)
                                        break
                            # Или по image_url
                            elif op.image_url is not None:
                                for img in aggregate.images:
                                    if img.object_key == op.image_url:
                                        deleted_image_keys.append(img.object_key)
                                        break

                        elif op.action == "pass":
                            # Сохраняем по image_id
                            if op.image_id is not None:
                                for img in aggregate.images:
                                    if img.image_id == op.image_id:
                                        final_images.append(
                                            ProductImageAggregate(
                                                object_key=img.object_key,
                                                is_main=op.is_main or img.is_main,
                                                image_id=img.image_id,
                                            )
                                        )
                                        break
                            # Или по image_url
                            elif op.image_url is not None:
                                for img in aggregate.images:
                                    if img.object_key == op.image_url:
                                        final_images.append(
                                            ProductImageAggregate(
                                                object_key=img.object_key,
                                                is_main=op.is_main or img.is_main,
                                                image_id=img.image_id,
                                            )
                                        )
                                        break
                            # Если ни image_id, ни image_url не указаны — сохраняем все существующие
                            else:
                                for img in aggregate.images:
                                    if not any(f.image_id == img.image_id for f in final_images):
                                        final_images.append(
                                            ProductImageAggregate(
                                                object_key=img.object_key,
                                                is_main=op.is_main or img.is_main,
                                                image_id=img.image_id,
                                            )
                                        )

                        elif op.action == "to_create":
                            if op.image is not None and op.image_name is not None:
                                image_key = self.image_storage.build_key(folder="products", filename=op.image_name)
                                content_type = guess_content_type(op.image_name)
                                await self.image_storage.upload_bytes(
                                    data=op.image,
                                    key=image_key,
                                    content_type=content_type,
                                )
                                new_image_keys.append(image_key)
                                final_images.append(
                                    ProductImageAggregate(
                                        object_key=image_key,
                                        is_main=op.is_main,
                                        image_id=None,
                                    )
                                )

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
                        {"image_key": image.object_key, "is_main": image.is_main, "image_id": image.image_id}
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
                            image_id=image.image_id,
                            image_key=image.object_key,
                            image_url=self.image_storage.build_public_url(image.object_key),
                            is_main=image.is_main,
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
            for key in new_image_keys:
                await self.image_storage.delete_object(key)
            raise

        for key in deleted_image_keys:
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
