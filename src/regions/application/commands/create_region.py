from typing import Any

from src.regions.application.dto.audit import RegionAuditDTO
from src.regions.application.dto.region import (
    RegionCreateDTO,
    RegionReadDTO,
)
from src.regions.domain.aggregates.region import RegionAggregate
from src.regions.domain.events.region_events import (
    RegionCreatedEvent,
)
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class CreateRegionCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        dto: RegionCreateDTO,
        user: User,
    ) -> RegionReadDTO:

        async with self.uow:
            aggregate = RegionAggregate(
                name=dto.name,
                parent_id=dto.parent_id,
            )

            await self.repository.create(aggregate)

            await self.audit_repository.log(
                RegionAuditDTO(
                    region_id=aggregate.id,
                    action="create",
                    old_data=None,
                    new_data={
                        "name": aggregate.name,
                        "parent_id": aggregate.parent_id,
                    },
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            result = RegionReadDTO(
                id=aggregate.id,
                name=aggregate.name,
                parent_id=aggregate.parent_id,
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
        aggregate: RegionAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, RegionCreatedEvent):
                events.extend(self._build_region_created_events(aggregate))

        return events

    def _build_region_created_events(
        self,
        aggregate: RegionAggregate,
    ) -> list[dict[str, Any]]:
        """Построить события для созданного региона."""
        return [
            build_event(
                event_type="crud",
                method="create",
                app="regions",
                entity="region",
                entity_id=aggregate.id,
                data={
                    "region_id": aggregate.id,
                    "fields": {
                        "name": aggregate.name,
                        "parent_id": aggregate.parent_id,
                    },
                },
            ),
        ]
