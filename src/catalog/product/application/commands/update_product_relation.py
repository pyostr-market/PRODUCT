from typing import Any

from src.catalog.product.application.dto.product_relation import (
    ProductRelationReadDTO,
    ProductRelationUpdateDTO,
)
from src.catalog.product.domain.aggregates.product_relation import (
    DomainEvent,
    ProductRelationAggregate,
    ProductRelationUpdatedEvent,
)
from src.catalog.product.domain.exceptions import ProductRelationNotFound
from src.catalog.product.domain.repository.audit import ProductAuditRepository
from src.catalog.product.domain.repository.product_relation import ProductRelationRepository
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class UpdateProductRelationCommand:
    """Команда для обновления связи между товарами."""

    def __init__(
        self,
        repository: ProductRelationRepository,
        audit_repository: ProductAuditRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        relation_id: int,
        dto: ProductRelationUpdateDTO,
        user: User,
    ) -> ProductRelationReadDTO:
        """Выполнить команду обновления связи."""
        async with self.uow:
            aggregate = await self.repository.get(relation_id)

            if not aggregate:
                raise ProductRelationNotFound()

            # Сохраняем старое состояние для аудита
            old_data = self._capture_state(aggregate)

            # Применяем изменения через агрегат
            aggregate.update(
                relation_type=dto.relation_type,
                sort_order=dto.sort_order,
            )

            # Сохраняем агрегат
            await self.repository.update(aggregate)

            # Получаем доменные события
            domain_events = aggregate.get_events()

            # Новое состояние для аудита
            new_data = self._capture_state(aggregate)

            # Логируем аудит только если данные изменились
            if old_data != new_data:
                await self.audit_repository.log(
                    self._create_audit_dto(aggregate, old_data, new_data, user),
                )

            result = self._to_read_dto(aggregate)

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events, old_data, new_data)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _capture_state(self, aggregate: ProductRelationAggregate) -> dict[str, Any]:
        """Зафиксировать текущее состояние агрегата."""
        return {
            "product_id": aggregate.product_id,
            "related_product_id": aggregate.related_product_id,
            "relation_type": aggregate.relation_type,
            "sort_order": aggregate.sort_order,
        }

    def _create_audit_dto(
        self,
        aggregate: ProductRelationAggregate,
        old_data: dict[str, Any],
        new_data: dict[str, Any],
        user: User,
    ) -> Any:
        """Создать DTO для audit лога."""
        from dataclasses import dataclass

        @dataclass
        class ProductRelationAuditDTO:
            relation_id: int
            action: str
            old_data: dict
            new_data: dict
            user_id: int
            fio: str

        return ProductRelationAuditDTO(
            relation_id=aggregate.id,
            action="update",
            old_data=old_data,
            new_data=new_data,
            user_id=user.id,
            fio=user.fio,
        )

    def _build_domain_events(
        self,
        aggregate: ProductRelationAggregate,
        domain_events: list[DomainEvent],
        old_data: dict[str, Any],
        new_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ProductRelationUpdatedEvent):
                events.append(
                    build_event(
                        event_type="crud",
                        method="update",
                        app="products",
                        entity="product_relation",
                        entity_id=aggregate.id,
                        data={
                            "relation_id": aggregate.id,
                            "changed_fields": event.changed_fields,
                        },
                    )
                )

        return events

    def _to_read_dto(self, aggregate: ProductRelationAggregate) -> ProductRelationReadDTO:
        """Преобразовать агрегат в DTO для чтения."""
        return ProductRelationReadDTO(
            id=aggregate.id,
            product_id=aggregate.product_id,
            related_product_id=aggregate.related_product_id,
            relation_type=aggregate.relation_type,
            sort_order=aggregate.sort_order,
        )
