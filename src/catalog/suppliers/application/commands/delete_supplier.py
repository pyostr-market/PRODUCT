from typing import Any

from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.catalog.suppliers.domain.events.supplier_events import (
    SupplierDeletedEvent,
)
from src.catalog.suppliers.domain.exceptions import SupplierNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class DeleteSupplierCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        supplier_id: int,
        user: User,
    ) -> bool:

        async with self.uow:
            aggregate = await self.repository.get(supplier_id)

            if not aggregate:
                raise SupplierNotFound()

            old_data = {
                "name": aggregate.name,
                "contact_email": aggregate.contact_email,
                "phone": aggregate.phone,
            }

            # Записываем доменное событие перед удалением
            self._record_deleted_event(aggregate)

            await self.repository.delete(supplier_id)

            await self.audit_repository.log(
                SupplierAuditDTO(
                    supplier_id=supplier_id,
                    action="delete",
                    old_data=old_data,
                    new_data=None,
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            # Получаем доменные события
            domain_events = aggregate.get_events()

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return True

    def _record_deleted_event(self, aggregate: SupplierAggregate):
        """Записать событие удаления."""
        aggregate._record_event(SupplierDeletedEvent(
            supplier_id=aggregate.id,
        ))

    def _build_domain_events(
        self,
        aggregate: SupplierAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, SupplierDeletedEvent):
                events.append(self._build_supplier_deleted_event(aggregate))

        return events

    def _build_supplier_deleted_event(
        self,
        aggregate: SupplierAggregate,
    ) -> dict[str, Any]:
        """Построить событие для удаленного поставщика."""
        return build_event(
            event_type="crud",
            method="delete",
            app="suppliers",
            entity="supplier",
            entity_id=aggregate.id,
            data={"supplier_id": aggregate.id},
        )
