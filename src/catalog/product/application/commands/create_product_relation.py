from typing import Any

from src.catalog.product.application.dto.product_relation import (
    ProductRelationCreateDTO,
    ProductRelationReadDTO,
)
from src.catalog.product.domain.aggregates.product_relation import (
    DomainEvent,
    ProductRelationAggregate,
    ProductRelationCreatedEvent,
)
from src.catalog.product.domain.exceptions import (
    ProductRelationAlreadyExists,
    ProductRelationInvalidProduct,
    ProductRelationSelfReference,
)
from src.catalog.product.domain.repository.audit import ProductAuditRepository
from src.catalog.product.domain.repository.product import ProductRepository
from src.catalog.product.domain.repository.product_relation import ProductRelationRepository
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class CreateProductRelationCommand:
    """Команда для создания связи между товарами."""

    def __init__(
        self,
        repository: ProductRelationRepository,
        product_repository: ProductRepository,
        audit_repository: ProductAuditRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.product_repository = product_repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, dto: ProductRelationCreateDTO, user: User) -> ProductRelationReadDTO:
        """Выполнить команду создания связи."""
        # Проверка: связь товара с самим собой не допускается
        if dto.product_id == dto.related_product_id:
            raise ProductRelationSelfReference()

        # Проверка: оба товара должны существовать
        product = await self.product_repository.get(dto.product_id)
        related_product = await self.product_repository.get(dto.related_product_id)

        if not product:
            raise ProductRelationInvalidProduct(details={"invalid_product_id": dto.product_id})

        if not related_product:
            raise ProductRelationInvalidProduct(
                details={"invalid_related_product_id": dto.related_product_id}
            )

        # Проверка: связь не должна существовать
        exists = await self.repository.exists(
            dto.product_id,
            dto.related_product_id,
            dto.relation_type,
        )
        if exists:
            raise ProductRelationAlreadyExists()

        async with self.uow:
            aggregate = ProductRelationAggregate(
                product_id=dto.product_id,
                related_product_id=dto.related_product_id,
                relation_type=dto.relation_type,
                sort_order=dto.sort_order,
            )

            await self.repository.create(aggregate)

            # Получаем доменные события из агрегата
            domain_events = aggregate.get_events()

            # Логируем в audit
            await self.audit_repository.log(
                self._create_audit_dto(aggregate, user),
            )

            result = self._to_read_dto(aggregate)

        # Публикуем события
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _create_audit_dto(
        self,
        aggregate: ProductRelationAggregate,
        user: User,
    ) -> Any:
        """Создать DTO для audit лога."""
        from dataclasses import dataclass

        @dataclass
        class ProductRelationAuditDTO:
            relation_id: int
            action: str
            old_data: None
            new_data: dict
            user_id: int
            fio: str

        return ProductRelationAuditDTO(
            relation_id=aggregate.id,
            action="create",
            old_data=None,
            new_data={
                "product_id": aggregate.product_id,
                "related_product_id": aggregate.related_product_id,
                "relation_type": aggregate.relation_type,
                "sort_order": aggregate.sort_order,
            },
            user_id=user.id,
            fio=user.fio,
        )

    def _build_domain_events(
        self,
        aggregate: ProductRelationAggregate,
        domain_events: list[DomainEvent],
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ProductRelationCreatedEvent):
                events.append(
                    build_event(
                        event_type="crud",
                        method="create",
                        app="products",
                        entity="product_relation",
                        entity_id=aggregate.id,
                        data={
                            "relation_id": aggregate.id,
                            "product_id": aggregate.product_id,
                            "related_product_id": aggregate.related_product_id,
                            "relation_type": aggregate.relation_type,
                            "sort_order": aggregate.sort_order,
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
