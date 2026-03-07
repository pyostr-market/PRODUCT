from typing import Any

from src.cms.application.dto.cms_dto import PageBlockReadDTO, PageReadDTO, PageUpdateDTO
from src.cms.domain.aggregates.page import PageAggregate
from src.cms.domain.repository.page import PageRepository
from src.cms.domain.services.page_slug_uniqueness_service import PageSlugUniquenessService
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class UpdatePageCommand:
    """Command для обновления страницы."""

    def __init__(
        self,
        repository: PageRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
        slug_uniqueness_service: PageSlugUniquenessService,
    ):
        self._repository = repository
        self._uow = uow
        self._event_bus = event_bus
        self._slug_uniqueness_service = slug_uniqueness_service

    async def execute(self, page_id: int, dto: PageUpdateDTO) -> PageReadDTO:
        """
        Выполнить команду обновления страницы.
        
        Args:
            page_id: ID страницы
            dto: Данные для обновления
            
        Returns:
            DTO обновленной страницы
            
        Raises:
            PageNotFound: Если страница не найдена
            PageSlugAlreadyExists: Если slug уже существует
        """
        # Загружаем страницу
        aggregate = await self._repository.get_by_id(page_id)
        if not aggregate:
            from src.cms.domain.exceptions import PageNotFound
            raise PageNotFound()

        try:
            async with self._uow:
                # Проверяем slug на уникальность если он меняется (через Domain Service)
                if dto.slug and dto.slug != aggregate.slug:
                    await self._slug_uniqueness_service.ensure_slug_is_unique(
                        dto.slug, exclude_id=page_id
                    )
                    aggregate.change_slug(dto.slug)

                # Обновляем title
                if dto.title:
                    aggregate.change_title(dto.title)

                # Обновляем статус публикации
                if dto.is_published is not None:
                    if dto.is_published:
                        aggregate.publish()
                    else:
                        aggregate.unpublish()

                # Сохраняем
                await self._repository.update(aggregate)

                # Получаем доменные события
                domain_events = aggregate.get_events()

            # Публикуем события
            events = self._build_events(aggregate, domain_events)
            if events:
                self._event_bus.publish_many_nowait(events)

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
        from src.cms.domain.events.cms_events import (
            PagePublishedEvent,
            PageSlugChangedEvent,
            PageTitleChangedEvent,
            PageUnpublishedEvent,
        )

        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, PageTitleChangedEvent):
                events.append(build_event(
                    event_type="crud",
                    method="update",
                    app="cms",
                    entity="page",
                    entity_id=aggregate.id,
                    data={
                        "page_id": aggregate.id,
                        "field": "title",
                        "old_value": event.old_title,
                        "new_value": event.new_title,
                    },
                ))
            elif isinstance(event, PageSlugChangedEvent):
                events.append(build_event(
                    event_type="crud",
                    method="update",
                    app="cms",
                    entity="page",
                    entity_id=aggregate.id,
                    data={
                        "page_id": aggregate.id,
                        "field": "slug",
                        "old_value": event.old_slug,
                        "new_value": event.new_slug,
                    },
                ))
            elif isinstance(event, PagePublishedEvent):
                events.append(build_event(
                    event_type="crud",
                    method="publish",
                    app="cms",
                    entity="page",
                    entity_id=aggregate.id,
                    data={"page_id": aggregate.id},
                ))
            elif isinstance(event, PageUnpublishedEvent):
                events.append(build_event(
                    event_type="crud",
                    method="unpublish",
                    app="cms",
                    entity="page",
                    entity_id=aggregate.id,
                    data={"page_id": aggregate.id},
                ))

        return events

    def _to_read_dto(self, aggregate: PageAggregate) -> PageReadDTO:
        """Преобразовать агрегат в read DTO."""
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
