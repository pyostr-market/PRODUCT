from typing import Any

from src.catalog.product.domain.aggregates.product_relation import (
    DomainEvent,
    ProductRelationAggregate,
    ProductRelationDeletedEvent,
)
from src.catalog.product.domain.exceptions import ProductRelationNotFound
from src.catalog.product.domain.repository.audit import ProductAuditRepository
from src.catalog.product.domain.repository.product_relation import ProductRelationRepository
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class DeleteProductRelationCommand:
    """Команда для удаления связи между товарами."""

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

    async def execute(self, relation_id: int, user: User) -> bool:
        """Выполнить команду удаления связи."""
        old_data: dict[str, Any] | None = None
        aggregate: ProductRelationAggregate | None = None

        async with self.uow:
            aggregate = await self.repository.get(relation_id)

            if not aggregate:
                raise ProductRelationNotFound()

            old_data = {
                "product_id": aggregate.product_id,
                "related_product_id": aggregate.related_product_id,
                "relation_type": aggregate.relation_type,
                "sort_order": aggregate.sort_order,
            }

            # Записываем доменное событие перед удалением
            aggregate._record_event(ProductRelationDeletedEvent(relation_id=relation_id))
            domain_events = aggregate.get_events()

            await self.repository.delete(relation_id)

            await self.audit_repository.log(
                self._create_audit_dto(aggregate, old_data, user),
            )

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events, old_data)
        if events:
            self.event_bus.publish_many_nowait(events)

        return True

    def _create_audit_dto(
        self,
        aggregate: ProductRelationAggregate,
        old_data: dict[str, Any],
        user: User,
    ) -> Any:
        """Создать DTO для audit лога."""
        from dataclasses import dataclass

        @dataclass
        class ProductRelationAuditDTO:
            relation_id: int
            action: str
            old_data: dict
            new_data: None
            user_id: int
            fio: str

        return ProductRelationAuditDTO(
            relation_id=aggregate.id,
            action="delete",
            old_data=old_data,
            new_data=None,
            user_id=user.id,
            fio=user.fio,
        )

    def _build_domain_events(
        self,
        aggregate: ProductRelationAggregate,
        domain_events: list[DomainEvent],
        old_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ProductRelationDeletedEvent):
                events.append(
                    build_event(
                        event_type="crud",
                        method="delete",
                        app="products",
                        entity="product_relation",
                        entity_id=aggregate.id,
                        data={
                            "relation_id": aggregate.id,
                            "product_id": aggregate.product_id,
                            "related_product_id": aggregate.related_product_id,
                        },
                    )
                )

        return events
