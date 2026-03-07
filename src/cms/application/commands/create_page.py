from typing import Any

from src.cms.application.dto.cms_dto import PageCreateDTO, PageReadDTO
from src.cms.domain.aggregates.page import PageAggregate
from src.cms.domain.events.cms_events import PageCreatedEvent
from src.cms.domain.repository.page import PageRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class CreatePageCommand:
    """Command для создания страницы."""

    def __init__(
        self,
        repository: PageRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, dto: PageCreateDTO) -> PageReadDTO:
        # Проверяем уникальность slug
        if await self.repository.exists_by_slug(dto.slug):
            from src.cms.domain.exceptions import PageSlugAlreadyExists
            raise PageSlugAlreadyExists(dto.slug)

        try:
            async with self.uow:
                # Создаем агрегат
                aggregate = PageAggregate(
                    slug=dto.slug,
                    title=dto.title,
                    is_published=dto.is_published,
                )

                # Добавляем блоки если есть
                if dto.blocks:
                    for block_dto in dto.blocks:
                        aggregate.add_block(
                            block_type=block_dto.block_type if hasattr(block_dto, 'block_type') else 'text',
                            data=block_dto.data or {},
                            order=block_dto.ordering if hasattr(block_dto, 'ordering') else 0,
                        )

                # Сохраняем
                await self.repository.create(aggregate)

                # Получаем доменные события
                domain_events = aggregate.get_events()

            # Публикуем события
            events = self._build_events(aggregate, domain_events)
            if events:
                self.event_bus.publish_many_nowait(events)

            # Возвращаем DTO
            return self._to_read_dto(aggregate)

        except Exception:
            raise

    def _build_events(
        self,
        aggregate: PageAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, PageCreatedEvent):
                events.append(build_event(
                    event_type="crud",
                    method="create",
                    app="cms",
                    entity="page",
                    entity_id=aggregate.id,
                    data={
                        "page_id": aggregate.id,
                        "slug": aggregate.slug,
                        "title": aggregate.title,
                    },
                ))

        return events

    def _to_read_dto(self, aggregate: PageAggregate) -> PageReadDTO:
        """Преобразовать агрегат в read DTO."""
        from src.cms.application.dto.cms_dto import PageBlockReadDTO

        return PageReadDTO(
            id=aggregate.id,
            slug=aggregate.slug,
            title=aggregate.title,
            is_published=aggregate.is_published,
            blocks=[
                PageBlockReadDTO(
                    id=block.id,
                    page_id=block.page_id,
                    block_type=block.block_type,
                    order=block.order,
                    data=block.data.data,
                    is_active=block.is_active,
                )
                for block in aggregate.blocks
            ],
        )
