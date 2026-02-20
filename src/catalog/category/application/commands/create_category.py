from src.catalog.category.application.dto.audit import CategoryAuditDTO
from src.catalog.category.application.dto.category import CategoryCreateDTO, CategoryImageReadDTO, CategoryReadDTO
from src.catalog.category.domain.aggregates.category import CategoryAggregate, CategoryImageAggregate
from src.core.auth.schemas.user import User
from src.core.services.images import ImageStorageService
from src.core.services.images.storage import guess_content_type


class CreateCategoryCommand:

    def __init__(self, repository, audit_repository, uow, image_storage: ImageStorageService):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage

    async def execute(
        self,
        dto: CategoryCreateDTO,
        user: User,
    ) -> CategoryReadDTO:
        uploaded_images: list[CategoryImageAggregate] = []
        uploaded_keys: list[str] = []

        for image in dto.images:
            image_key = self.image_storage.build_key(folder="categories", filename=image.image_name)
            content_type = guess_content_type(image.image_name)
            await self.image_storage.upload_bytes(data=image.image, key=image_key, content_type=content_type)
            uploaded_keys.append(image_key)
            uploaded_images.append(CategoryImageAggregate(object_key=image_key, ordering=image.ordering))

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
                                {"image_key": image.object_key, "ordering": image.ordering}
                                for image in aggregate.images
                            ],
                        },
                        user_id=user.id,
                    )
                )

                return CategoryReadDTO(
                    id=aggregate.id,
                    name=aggregate.name,
                    description=aggregate.description,
                    parent_id=aggregate.parent_id,
                    manufacturer_id=aggregate.manufacturer_id,
                    images=[
                        CategoryImageReadDTO(
                            ordering=image.ordering,
                            image_key=image.object_key,
                            image_url=self.image_storage.build_public_url(image.object_key),
                        )
                        for image in sorted(aggregate.images, key=lambda i: i.ordering)
                    ],
                )
        except Exception:
            for key in uploaded_keys:
                await self.image_storage.delete_object(key)
            raise
