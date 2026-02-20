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
from src.core.services.images import ImageStorageService
from src.core.services.images.storage import guess_content_type


class UpdateProductCommand:

    def __init__(self, repository, audit_repository, uow, image_storage: ImageStorageService):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage

    async def execute(self, product_id: int, dto, user: User) -> ProductReadDTO:
        old_image_keys: list[str] = []
        new_image_keys: list[str] = []

        try:
            async with self.uow:
                aggregate = await self.repository.get(product_id)

                if not aggregate:
                    raise ProductNotFound()

                old_image_keys = [image.object_key for image in aggregate.images]

                old_data = {
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

                aggregate.update(
                    name=dto.name,
                    description=dto.description,
                    price=dto.price,
                    category_id=dto.category_id,
                    supplier_id=dto.supplier_id,
                    product_type_id=dto.product_type_id,
                )

                if dto.images is not None:
                    mapped_images: list[ProductImageAggregate] = []
                    for image in dto.images:
                        image_key = self.image_storage.build_key(folder="products", filename=image.image_name)
                        content_type = guess_content_type(image.image_name)
                        await self.image_storage.upload_bytes(
                            data=image.image,
                            key=image_key,
                            content_type=content_type,
                        )
                        new_image_keys.append(image_key)
                        mapped_images.append(
                            ProductImageAggregate(object_key=image_key, is_main=image.is_main)
                        )
                    aggregate.replace_images(mapped_images)

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

                if old_data != new_data:
                    await self.audit_repository.log(
                        ProductAuditDTO(
                            product_id=aggregate.id,
                            action="update",
                            old_data=old_data,
                            new_data=new_data,
                            user_id=user.id,
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

        if dto.images is not None:
            new_keys_set = set(new_image_keys)
            for key in old_image_keys:
                if key not in new_keys_set:
                    await self.image_storage.delete_object(key)

        return result
