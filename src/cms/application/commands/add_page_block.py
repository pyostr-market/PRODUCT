from typing import Any

from src.cms.application.dto.cms_dto import PageBlockDTO
from src.cms.domain.aggregates.page import PageAggregate
from src.cms.domain.aggregates.page_block import PageBlockAggregate
from src.cms.domain.repository.page import PageRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class AddPageBlockCommand:
    """Command для добавления блока на страницу."""

    def __init__(
        self,
        repository: PageRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        page_id: int,
        block_type: str,
        data: dict[str, Any],
        order: int | None = None,
    ) -> int:
        # Загружаем страницу
        aggregate = await self.repository.get_by_id(page_id)
        if not aggregate:
            from src.cms.domain.exceptions import PageNotFound
            raise PageNotFound()

        try:
            async with self.uow:
                # Добавляем блок
                block = aggregate.add_block(
                    block_type=block_type,
                    data=data,
                    order=order,
                )

                # Сохраняем
                await self.repository.update(aggregate)

                # Получаем доменные события
                domain_events = block.get_events()

            # Публикуем события
            events = self._build_events(aggregate, block, domain_events)
            if events:
                self.event_bus.publish_many_nowait(events)

            return block.id or 0

        except Exception:
            raise

    def _build_events(
        self,
        aggregate: PageAggregate,
        block: PageBlockAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        from src.cms.domain.events.cms_events import PageBlockAddedEvent

        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, PageBlockAddedEvent):
                events.append(build_event(
                    event_type="crud",
                    method="create",
                    app="cms",
                    entity="page_block",
                    entity_id=block.id,
                    data={
                        "page_id": aggregate.id,
                        "block_id": block.id,
                        "block_type": block.block_type,
                    },
                ))

        return events
