from typing import Any

from src.catalog.product.application.dto.audit import ProductAuditDTO
from src.catalog.product.application.dto.product import (
    ProductAttributeReadDTO,
    ProductImageReadDTO,
    ProductReadDTO,
)
from src.catalog.product.application.services.related_entity_loader import (
    RelatedEntityLoader,
)
from src.catalog.product.domain.aggregates.product import (
    ProductAggregate,
    ProductAttributeAggregate,
    ProductImageAggregate,
    ProductImageOperation,
)
from src.catalog.product.domain.events.product_events import (
    DomainEvent,
    PriceChangedEvent,
    ProductImageAddedEvent,
    ProductImageRemovedEvent,
    ProductNameChangedEvent,
    ProductUpdatedEvent,
)
from src.catalog.product.domain.exceptions import ProductNotFound
from src.catalog.product.domain.repository.audit import ProductAuditRepository
from src.catalog.product.domain.repository.product import ProductRepository
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event
from src.core.services.images.storage import S3ImageStorageService
from src.uploads.domain.repository.upload_history import UploadHistoryRepository


class UpdateProductCommand:

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

    async def execute(self, product_id: int, dto, user: User) -> ProductReadDTO:
        async with self.uow:
            aggregate = await self.repository.get(product_id)

            if not aggregate:
                raise ProductNotFound()

            # Сохраняем старое состояние для аудита
            old_data = self._capture_state(aggregate)

            # Применяем изменения к агрегату
            self._apply_changes(aggregate, dto)

            # Применяем операции с изображениями
            if dto.images is not None:
                await self._apply_image_operations(aggregate, dto.images)

            # Применяем изменения атрибутов
            if dto.attributes is not None:
                aggregate.replace_attributes([
                    ProductAttributeAggregate(
                        name=attribute.name,
                        value=attribute.value,
                        is_filterable=attribute.is_filterable,
                    )
                    for attribute in dto.attributes
                ])

            # Сохраняем агрегат
            await self.repository.update(aggregate)

            # Получаем доменные события
            domain_events = aggregate.get_events()

            # Новое состояние для аудита
            new_data = self._capture_state(aggregate)

            # Логируем аудит только если данные изменились
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

            # Загружаем связанные данные через сервис
            category_dto, supplier_dto, product_type_dto = await self.entity_loader.load_all(
                aggregate.category_id,
                aggregate.supplier_id,
                aggregate.product_type_id,
            )

            result = self._to_read_dto(
                aggregate,
                category_dto,
                supplier_dto,
                product_type_dto,
            )

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events, old_data, new_data)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _apply_changes(
        self,
        aggregate: ProductAggregate,
        dto,
    ):
        """Применить изменения к агрегату через доменные методы."""
        aggregate.update(
            name=dto.name,
            description=dto.description,
            price=dto.price,
            category_id=dto.category_id,
            supplier_id=dto.supplier_id,
            product_type_id=dto.product_type_id,
        )

    async def _apply_image_operations(
        self,
        aggregate: ProductAggregate,
        image_ops,
    ):
        """Применить операции с изображениями через агрегат."""
        existing_images = list(aggregate.images)
        
        # Загружаем данные для новых изображений
        for op in image_ops:
            if op.action == "create" and op.upload_id is not None:
                upload_record = await self.upload_history_repository.get(op.upload_id)
                if upload_record:
                    op.object_key = upload_record.file_path

        # Применяем операции через агрегат
        final_images = aggregate.apply_image_operations(
            operations=[
                ProductImageOperation(
                    action=op.action,
                    upload_id=op.upload_id,
                    is_main=op.is_main,
                    ordering=op.ordering,
                )
                for op in image_ops
            ],
            existing_images=existing_images,
        )

        # Обновляем изображения в агрегате
        aggregate.replace_images(final_images)

    def _capture_state(self, aggregate: ProductAggregate) -> dict[str, Any]:
        """Зафиксировать текущее состояние агрегата."""
        return {
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

    def _build_domain_events(
        self,
        aggregate: ProductAggregate,
        domain_events: list[DomainEvent],
        old_data: dict[str, Any],
        new_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        changed_fields = {
            key: value
            for key, value in new_data.items()
            if old_data.get(key) != value
        }

        if changed_fields:
            # Основное CRUD событие
            events.append(
                build_event(
                    event_type="crud",
                    method="update",
                    app="products",
                    entity="product",
                    entity_id=aggregate.id,
                    data={
                        "product_id": aggregate.id,
                        "fields": changed_fields,
                    },
                )
            )

            # Дополнительные события для специфичных полей
            for event in domain_events:
                if isinstance(event, PriceChangedEvent):
                    events.append(
                        build_event(
                            event_type="field_update",
                            method="price_update",
                            app="products",
                            entity="product",
                            entity_id=aggregate.id,
                            data={
                                "product_id": aggregate.id,
                                "price": {
                                    "old": str(event.old_price),
                                    "new": str(event.new_price),
                                },
                            },
                        )
                    )
                elif isinstance(event, ProductNameChangedEvent):
                    pass  # Уже включено в основное событие

            # События для изображений
            image_events = [e for e in domain_events if isinstance(e, (ProductImageAddedEvent, ProductImageRemovedEvent))]
            if image_events or "images" in changed_fields:
                events.append(
                    build_event(
                        event_type="field_update",
                        method="update",
                        app="images",
                        entity="product_images",
                        entity_id=aggregate.id,
                        data={
                            "product_id": aggregate.id,
                            "images": changed_fields.get("images", []),
                        },
                    )
                )

            # Событие для product_type
            if "product_type_id" in changed_fields:
                events.append(
                    build_event(
                        event_type="field_update",
                        method="update",
                        app="device_types",
                        entity="product_type",
                        entity_id=aggregate.id,
                        data={
                            "product_id": aggregate.id,
                            "product_type_id": {
                                "old": old_data.get("product_type_id"),
                                "new": changed_fields["product_type_id"],
                            },
                        },
                    )
                )

        return events

    def _to_read_dto(
        self,
        aggregate: ProductAggregate,
        category_dto,
        supplier_dto,
        product_type_dto,
    ) -> ProductReadDTO:
        """Преобразовать агрегат в DTO для чтения."""
        return ProductReadDTO(
            id=aggregate.id,
            name=aggregate.name,
            description=aggregate.description,
            price=aggregate.price,
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
            category=category_dto,
            supplier=supplier_dto,
            product_type=product_type_dto,
        )
