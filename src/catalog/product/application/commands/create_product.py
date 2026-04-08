from typing import Any

from src.catalog.product.application.dto.audit import ProductAuditDTO
from src.catalog.product.application.dto.product import (
    ProductAttributeReadDTO,
    ProductImageReadDTO,
    ProductRatingDTO,
    ProductReadDTO,
)
from src.catalog.product.application.services.related_entity_loader import (
    RelatedEntityLoader,
)
from src.catalog.product.domain.aggregates.product import (
    ProductAggregate,
    ProductAttributeAggregate,
    ProductImageAggregate,
)
from src.catalog.product.domain.events.product_events import (
    DomainEvent,
    ProductAttributeAddedEvent,
    ProductCreatedEvent,
    ProductImageAddedEvent,
)
from src.catalog.product.domain.repository.audit import ProductAuditRepository
from src.catalog.product.domain.repository.product import ProductRepository
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event
from src.core.services.images.storage import S3ImageStorageService
from src.uploads.domain.repository.upload_history import UploadHistoryRepository


class CreateProductCommand:

    def __init__(
        self,
        repository: ProductRepository,
        audit_repository: ProductAuditRepository,
        uow: UnitOfWork,
        image_storage: S3ImageStorageService,
        event_bus: AsyncEventBus,
        upload_history_repository: UploadHistoryRepository,
        entity_loader: RelatedEntityLoader,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.image_storage = image_storage
        self.event_bus = event_bus
        self.upload_history_repository = upload_history_repository
        self.entity_loader = entity_loader

    async def execute(self, dto, user: User) -> ProductReadDTO:
        mapped_images: list[ProductImageAggregate] = []

        for image in dto.images:
            if not image.upload_id:
                from src.catalog.product.domain.exceptions import ProductInvalidImage
                raise ProductInvalidImage(details={"reason": "upload_id_required"})

            upload_record = await self.upload_history_repository.get(image.upload_id)

            if not upload_record:
                from src.catalog.product.domain.exceptions import ProductInvalidImage
                raise ProductInvalidImage(details={"reason": "upload_not_found", "upload_id": image.upload_id})

            mapped_images.append(
                ProductImageAggregate(
                    upload_id=upload_record.upload_id,
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
                is_groupable=attribute.is_groupable,
            )
            for attribute in dto.attributes
        ]

        async with self.uow:
            aggregate = ProductAggregate(
                name=dto.name,
                description=dto.description,
                price=dto.price,
                category_id=dto.category_id,
                supplier_id=dto.supplier_id,
                images=mapped_images,
                attributes=mapped_attributes,
            )

            await self.repository.create(aggregate)

            # Получаем доменные события из агрегата
            domain_events = aggregate.get_events()

            new_data = self._capture_state(aggregate)

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

            # Загружаем связанные данные через сервис
            category_dto, supplier_dto = await self.entity_loader.load_category_and_supplier(
                aggregate.category_id,
                aggregate.supplier_id,
            )

            result = self._to_read_dto(
                aggregate,
                category_dto,
                supplier_dto,
            )

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _capture_state(self, aggregate: ProductAggregate) -> dict[str, Any]:
        """Зафиксировать текущее состояние агрегата."""
        return {
            "name": aggregate.name,
            "description": aggregate.description,
            "price": str(aggregate.price),
            "category_id": aggregate.category_id,
            "supplier_id": aggregate.supplier_id,
            "images": [
                {"upload_id": image.upload_id, "is_main": image.is_main}
                for image in aggregate.images
            ],
            "attributes": [
                {
                    "name": attribute.name,
                    "value": attribute.value,
                    "is_filterable": attribute.is_filterable,
                    "is_groupable": attribute.is_groupable,
                }
                for attribute in aggregate.attributes
            ],
        }

    def _build_domain_events(
        self,
        aggregate: ProductAggregate,
        domain_events: list[DomainEvent],
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ProductCreatedEvent):
                events.extend(self._build_product_created_events(aggregate))
            elif isinstance(event, ProductImageAddedEvent):
                events.append(self._build_image_event("create", aggregate.id, event.upload_id))
            elif isinstance(event, ProductAttributeAddedEvent):
                pass  # Атрибуты не имеют отдельных событий в текущей реализации

        return events

    def _build_product_created_events(self, aggregate: ProductAggregate) -> list[dict[str, Any]]:
        """Построить события для созданного продукта."""
        return [
            build_event(
                event_type="crud",
                method="create",
                app="products",
                entity="product",
                entity_id=aggregate.id,
                data={
                    "product_id": aggregate.id,
                    "fields": {
                        "name": aggregate.name,
                        "description": aggregate.description,
                        "price": str(aggregate.price),
                        "category_id": aggregate.category_id,
                        "supplier_id": aggregate.supplier_id,
                    },
                },
            ),
            build_event(
                event_type="crud",
                method="create",
                app="images",
                entity="product_images",
                entity_id=aggregate.id,
                data={
                    "product_id": aggregate.id,
                    "images": [
                        {"upload_id": image.upload_id, "is_main": image.is_main}
                        for image in aggregate.images
                    ],
                },
            ),
        ]

    def _build_image_event(
        self,
        method: str,
        product_id: int,
        upload_id: int,
    ) -> dict[str, Any]:
        """Построить событие для изображения."""
        return build_event(
            event_type="crud",
            method=method,
            app="images",
            entity="product_images",
            entity_id=product_id,
            data={
                "product_id": product_id,
                "images": [{"upload_id": upload_id}],
            },
        )

    def _to_read_dto(
        self,
        aggregate: ProductAggregate,
        category_dto,
        supplier_dto,
    ) -> ProductReadDTO:
        """Преобразовать агрегат в DTO для чтения."""
        return ProductReadDTO(
            id=aggregate.id,
            name=aggregate.name,
            description=aggregate.description,
            price=aggregate.price,
            rating=ProductRatingDTO(value=None, count=0),
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
                    is_groupable=attribute.is_groupable,
                )
                for attribute in aggregate.attributes
            ],
            category=category_dto,
            supplier=supplier_dto,
        )
