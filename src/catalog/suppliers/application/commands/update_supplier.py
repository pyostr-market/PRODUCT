from typing import Any

from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.application.dto.supplier import (
    SupplierReadDTO,
    SupplierUpdateDTO,
)
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.catalog.suppliers.domain.events.supplier_events import (
    SupplierUpdatedEvent,
)
from src.catalog.suppliers.domain.exceptions import SupplierNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class UpdateSupplierCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        supplier_id: int,
        dto: SupplierUpdateDTO,
        user: User,
    ) -> SupplierReadDTO:

        async with self.uow:
            aggregate = await self.repository.get(supplier_id)

            if not aggregate:
                raise SupplierNotFound()

            old_data = {
                "name": aggregate.name,
                "contact_email": aggregate.contact_email,
                "phone": aggregate.phone,
            }

            aggregate.update(dto.name, dto.contact_email, dto.phone)
            await self.repository.update(aggregate)

            new_data = {
                "name": aggregate.name,
                "contact_email": aggregate.contact_email,
                "phone": aggregate.phone,
            }

            if old_data != new_data:
                await self.audit_repository.log(
                    SupplierAuditDTO(
                        supplier_id=aggregate.id,
                        action="update",
                        old_data=old_data,
                        new_data=new_data,
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

        changed_fields = {
            key: value
            for key, value in new_data.items()
            if old_data.get(key) != value
        }

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events, changed_fields)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _build_domain_events(
        self,
        aggregate: SupplierAggregate,
        domain_events: list,
        changed_fields: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, SupplierUpdatedEvent):
                events.append(self._build_supplier_updated_event(aggregate, changed_fields))

        if not events and changed_fields:
            events.append(self._build_supplier_updated_event(aggregate, changed_fields))

        return events

    def _build_supplier_updated_event(
        self,
        aggregate: SupplierAggregate,
        changed_fields: dict[str, Any],
    ) -> dict[str, Any]:
        """Построить событие для обновленного поставщика."""
        return build_event(
            event_type="crud",
            method="update",
            app="suppliers",
            entity="supplier",
            entity_id=aggregate.id,
            data={
                "supplier_id": aggregate.id,
                "fields": changed_fields,
            },
        )
