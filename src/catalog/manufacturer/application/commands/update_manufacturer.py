from typing import Any

from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.application.dto.manufacturer import (
    ManufacturerReadDTO,
    ManufacturerUpdateDTO,
)
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.catalog.manufacturer.domain.events.manufacturer_events import (
    ManufacturerUpdatedEvent,
)
from src.catalog.manufacturer.domain.exceptions import ManufacturerNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class UpdateManufacturerCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        manufacturer_id: int,
        dto: ManufacturerUpdateDTO,
        user: User,
    ) -> ManufacturerReadDTO:

        async with self.uow:
            aggregate = await self.repository.get(manufacturer_id)

            if not aggregate:
                raise ManufacturerNotFound()

            old_data = {
                "name": aggregate.name,
                "description": aggregate.description,
            }

            aggregate.update(dto.name, dto.description)

            await self.repository.update(aggregate)

            new_data = {
                "name": aggregate.name,
                "description": aggregate.description,
            }

            if old_data != new_data:
                await self.audit_repository.log(
                    ManufacturerAuditDTO(
                        manufacturer_id=aggregate.id,
                        action="update",
                        old_data=old_data,
                        new_data=new_data,
                        user_id=user.id,
                        fio=user.fio,
                    )
                )

            result = ManufacturerReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                description=aggregate.description,
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
        aggregate: ManufacturerAggregate,
        domain_events: list,
        changed_fields: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ManufacturerUpdatedEvent):
                events.append(self._build_manufacturer_updated_event(aggregate, changed_fields))

        if not events and changed_fields:
            events.append(self._build_manufacturer_updated_event(aggregate, changed_fields))

        return events

    def _build_manufacturer_updated_event(
        self,
        aggregate: ManufacturerAggregate,
        changed_fields: dict[str, Any],
    ) -> dict[str, Any]:
        """Построить событие для обновленного производителя."""
        return build_event(
            event_type="crud",
            method="update",
            app="manufacturers",
            entity="manufacturer",
            entity_id=aggregate.id,
            data={
                "manufacturer_id": aggregate.id,
                "fields": changed_fields,
            },
        )
