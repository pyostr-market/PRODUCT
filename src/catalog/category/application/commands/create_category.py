from typing import Any

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
from src.catalog.category.domain.events.category_events import (
    CategoryCreatedEvent,
    CategoryImageAddedEvent,
)
from src.catalog.category.infrastructure.services.related_data_loader import (
    CategoryRelatedDataLoader,
)
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event
from src.core.services.images import ImageStorageService


class CreateCategoryCommand:

    def __init__(
        self,
        repository,
        audit_repository,
        uow,
        image_storage: ImageStorageService,
        event_bus: AsyncEventBus,
        data_loader: CategoryRelatedDataLoader,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage
        self.event_bus = event_bus
        self.data_loader = data_loader

    async def execute(
        self,
        dto: CategoryCreateDTO,
        user: User,
    ) -> CategoryReadDTO:
        uploaded_images: list[CategoryImageAggregate] = []

        for image in dto.images:
            upload_id, object_key = await self.data_loader.get_upload_info(image.upload_id)
            
            uploaded_images.append(CategoryImageAggregate(
                upload_id=upload_id,
                ordering=image.ordering,
                object_key=object_key,
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

                # Загружаем данные для parent и manufacturer через сервис
                parent_dto = None
                if aggregate.parent_id:
                    parent_dto = await self.data_loader.get_parent_category(aggregate.parent_id)

                manufacturer_dto = None
                if aggregate.manufacturer_id:
                    manufacturer_dto = await self.data_loader.get_manufacturer(aggregate.manufacturer_id)

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

                # Получаем доменные события из агрегата
                domain_events = aggregate.get_events()

        except Exception:
            raise

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _build_domain_events(
        self,
        aggregate: CategoryAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, CategoryCreatedEvent):
                events.extend(self._build_category_created_events(aggregate))
            elif isinstance(event, CategoryImageAddedEvent):
                events.append(self._build_image_event("create", aggregate.id, event.upload_id))

        return events

    def _build_category_created_events(self, aggregate: CategoryAggregate) -> list[dict[str, Any]]:
        """Построить события для созданной категории."""
        return [
            build_event(
                event_type="crud",
                method="create",
                app="categories",
                entity="category",
                entity_id=aggregate.id,
                data={
                    "category_id": aggregate.id,
                    "fields": {
                        "name": aggregate.name,
                        "description": aggregate.description,
                        "parent_id": aggregate.parent_id,
                        "manufacturer_id": aggregate.manufacturer_id,
                    },
                },
            ),
            build_event(
                event_type="crud",
                method="create",
                app="images",
                entity="category_images",
                entity_id=aggregate.id,
                data={
                    "category_id": aggregate.id,
                    "images": [
                        {"upload_id": image.upload_id, "ordering": image.ordering}
                        for image in aggregate.images
                    ],
                },
            ),
        ]

    def _build_image_event(
        self,
        method: str,
        category_id: int,
        upload_id: int,
    ) -> dict[str, Any]:
        """Построить событие для изображения."""
        return build_event(
            event_type="crud",
            method=method,
            app="images",
            entity="category_images",
            entity_id=category_id,
            data={
                "category_id": category_id,
                "images": [{"upload_id": upload_id}],
            },
        )
