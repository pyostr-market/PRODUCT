from typing import Any

from src.regions.application.dto.audit import RegionAuditDTO
from src.regions.domain.aggregates.region import RegionAggregate
from src.regions.domain.events.region_events import (
    RegionDeletedEvent,
)
from src.regions.domain.exceptions import RegionNotFound
from src.core.auth.schemas.user import User
from src.core.events import AsyncEventBus, build_event


class DeleteRegionCommand:

    def __init__(self, repository, audit_repository, uow, event_bus: AsyncEventBus):
        self.repository = repository
        self.audit_repository = audit_repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        region_id: int,
        user: User,
    ) -> bool:

        async with self.uow:
            aggregate = await self.repository.get(region_id)

            if not aggregate:
                raise RegionNotFound()

            old_data = {
                "name": aggregate.name,
                "parent_id": aggregate.parent_id,
            }

            # Записываем доменное событие перед удалением
            self._record_deleted_event(aggregate)

            # Сначала записываем аудит-лог (пока регион ещё существует в БД)
            await self.audit_repository.log(
                RegionAuditDTO(
                    region_id=region_id,
                    action="delete",
                    old_data=old_data,
                    new_data=None,
                    user_id=user.id,
                    fio=user.fio,
                )
            )

            # Затем удаляем регион
            await self.repository.delete(region_id)

            # Получаем доменные события
            domain_events = aggregate.get_events()

        # Публикуем события на основе доменных событий
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return True

    def _record_deleted_event(self, aggregate: RegionAggregate):
        """Записать событие удаления."""
        aggregate._record_event(RegionDeletedEvent(
            region_id=aggregate.id,
        ))

    def _build_domain_events(
        self,
        aggregate: RegionAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, RegionDeletedEvent):
                events.append(self._build_region_deleted_event(aggregate))

        return events

    def _build_region_deleted_event(
        self,
        aggregate: RegionAggregate,
    ) -> dict[str, Any]:
        """Построить событие для удаленного региона."""
        return build_event(
            event_type="crud",
            method="delete",
            app="regions",
            entity="region",
            entity_id=aggregate.id,
            data={"region_id": aggregate.id},
        )
