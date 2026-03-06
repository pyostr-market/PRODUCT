from typing import Any

from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.catalog.manufacturer.domain.events.manufacturer_events import (
    ManufacturerDeletedEvent,
)
from src.catalog.manufacturer.domain.exceptions import ManufacturerNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class DeleteManufacturerCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        manufacturer_id: int,
        user: User,
    ) -> bool:
        async with self.uow:
            aggregate = await self.repository.get(manufacturer_id)

            if not aggregate:
                raise ManufacturerNotFound()

            old_data = {
                "name": aggregate.name,
                "description": aggregate.description,
            }

            await self.repository.delete(manufacturer_id)

            await self.audit_repository.log(
                ManufacturerAuditDTO(
                    manufacturer_id=manufacturer_id,
                    action="delete",
                    old_data=old_data,
                    new_data=None,
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            # Получаем доменные события из агрегата
            domain_events = aggregate.get_events()

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(manufacturer_id, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return True

    def _build_domain_events(
        self,
        manufacturer_id: int,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ManufacturerDeletedEvent):
                events.append(self._build_manufacturer_deleted_event(manufacturer_id))

        if not events:
            events.append(self._build_manufacturer_deleted_event(manufacturer_id))

        return events

    def _build_manufacturer_deleted_event(
        self,
        manufacturer_id: int,
    ) -> dict[str, Any]:
        """Построить событие для удаленного производителя."""
        return build_event(
            event_type="crud",
            method="delete",
            app="manufacturers",
            entity="manufacturer",
            entity_id=manufacturer_id,
            data={"manufacturer_id": manufacturer_id},
        )
