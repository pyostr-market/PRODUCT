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
from src.core.services.images import ImageStorageService
from src.core.services.images.storage import guess_content_type


class CreateProductCommand:

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

    async def execute(self, dto, user: User) -> ProductReadDTO:
        uploaded_keys: list[str] = []

        mapped_images: list[ProductImageAggregate] = []
        for image in dto.images:
            image_key = self.image_storage.build_key(folder="products", filename=image.image_name)
            content_type = guess_content_type(image.image_name)
            await self.image_storage.upload_bytes(data=image.image, key=image_key, content_type=content_type)
            uploaded_keys.append(image_key)
            mapped_images.append(
                ProductImageAggregate(object_key=image_key, is_main=image.is_main)
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
                        {"image_key": image.object_key, "is_main": image.is_main}
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
            for key in uploaded_keys:
                await self.image_storage.delete_object(key)
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
                            {"image_key": image.image_key, "is_main": image.is_main}
                            for image in result.images
                        ],
                    },
                ),
            ]
        )
        return result
