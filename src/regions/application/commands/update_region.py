from typing import Any

from src.regions.application.dto.audit import RegionAuditDTO
from src.regions.application.dto.region import (
    RegionReadDTO,
    RegionUpdateDTO,
)
from src.regions.domain.aggregates.region import RegionAggregate
from src.regions.domain.events.region_events import (
    RegionUpdatedEvent,
)
from src.regions.domain.exceptions import RegionNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class UpdateRegionCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        region_id: int,
        dto: RegionUpdateDTO,
        user: User,
    ) -> RegionReadDTO:

        async with self.uow:
            aggregate = await self.repository.get(region_id)

            if not aggregate:
                raise RegionNotFound()

            old_data = {
                "name": aggregate.name,
                "parent_id": aggregate.parent_id,
            }

            aggregate.update(dto.name, dto.parent_id)
            await self.repository.update(aggregate)

            new_data = {
                "name": aggregate.name,
                "parent_id": aggregate.parent_id,
            }

            if old_data != new_data:
                await self.audit_repository.log(
                    RegionAuditDTO(
                        region_id=aggregate.id,
                        action="update",
                        old_data=old_data,
                        new_data=new_data,
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
        aggregate: RegionAggregate,
        domain_events: list,
        changed_fields: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, RegionUpdatedEvent):
                events.append(self._build_region_updated_event(aggregate, changed_fields))

        if not events and changed_fields:
            events.append(self._build_region_updated_event(aggregate, changed_fields))

        return events

    def _build_region_updated_event(
        self,
        aggregate: RegionAggregate,
        changed_fields: dict[str, Any],
    ) -> dict[str, Any]:
        """Построить событие для обновленного региона."""
        return build_event(
            event_type="crud",
            method="update",
            app="regions",
            entity="region",
            entity_id=aggregate.id,
            data={
                "region_id": aggregate.id,
                "fields": changed_fields,
            },
        )
