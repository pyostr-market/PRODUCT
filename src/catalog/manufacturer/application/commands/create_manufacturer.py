from typing import Any

from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.application.dto.manufacturer import (
    ManufacturerCreateDTO,
    ManufacturerReadDTO,
)
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.catalog.manufacturer.domain.events.manufacturer_events import (
    ManufacturerCreatedEvent,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class CreateManufacturerCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        dto: ManufacturerCreateDTO,
        user: User,
    ) -> ManufacturerReadDTO:

        async with self.uow:
            aggregate = ManufacturerAggregate(
                name=dto.name,
                description=dto.description,
            )

            await self.repository.create(aggregate)

            await self.audit_repository.log(
                ManufacturerAuditDTO(
                    manufacturer_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "description": aggregate.description,
                    },
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

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _build_domain_events(
        self,
        aggregate: ManufacturerAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, ManufacturerCreatedEvent):
                events.extend(self._build_manufacturer_created_events(aggregate))

        return events

    def _build_manufacturer_created_events(
        self,
        aggregate: ManufacturerAggregate,
    ) -> list[dict[str, Any]]:
        """Построить события для созданного производителя."""
        return [
            build_event(
                event_type="crud",
                method="create",
                app="manufacturers",
                entity="manufacturer",
                entity_id=aggregate.id,
                data={
                    "manufacturer_id": aggregate.id,
                    "fields": {
                        "name": aggregate.name,
                        "description": aggregate.description,
                    },
                },
            ),
        ]
