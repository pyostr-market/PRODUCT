from typing import Any

from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.application.dto.supplier import (
    SupplierCreateDTO,
    SupplierReadDTO,
)
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.catalog.suppliers.domain.events.supplier_events import (
    SupplierCreatedEvent,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class CreateSupplierCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        dto: SupplierCreateDTO,
        user: User,
    ) -> SupplierReadDTO:

        async with self.uow:
            aggregate = SupplierAggregate(
                name=dto.name,
                contact_email=dto.contact_email,
                phone=dto.phone,
            )

            await self.repository.create(aggregate)

            await self.audit_repository.log(
                SupplierAuditDTO(
                    supplier_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "contact_email": aggregate.contact_email,
                        "phone": aggregate.phone,
                    },
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            result = SupplierReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                contact_email=aggregate.contact_email,
                phone=aggregate.phone,
            )

            # Получаем доменные события из агрегата
            domain_events = aggregate.get_events()

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _build_domain_events(
        self,
        aggregate: SupplierAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, SupplierCreatedEvent):
                events.extend(self._build_supplier_created_events(aggregate))

        return events

    def _build_supplier_created_events(
        self,
        aggregate: SupplierAggregate,
    ) -> list[dict[str, Any]]:
        """Построить события для созданного поставщика."""
        return [
            build_event(
                event_type="crud",
                method="create",
                app="suppliers",
                entity="supplier",
                entity_id=aggregate.id,
                data={
                    "supplier_id": aggregate.id,
                    "fields": {
                        "name": aggregate.name,
                        "contact_email": aggregate.contact_email,
                        "phone": aggregate.phone,
                    },
                },
            ),
        ]
