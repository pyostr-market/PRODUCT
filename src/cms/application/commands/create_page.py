from typing import Any

from src.cms.application.dto.cms_dto import PageCreateDTO, PageReadDTO
from src.cms.domain.aggregates.page import PageAggregate
from src.cms.domain.events.cms_events import PageCreatedEvent
from src.cms.domain.repository.page import PageRepository
from src.cms.domain.services.page_slug_uniqueness_service import (
    PageSlugUniquenessService,
)
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class CreatePageCommand:
    """Command для создания страницы."""

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

    async def execute(self, dto: PageCreateDTO) -> PageReadDTO:
        """
        Выполнить команду создания страницы.
        
        Args:
            dto: Данные для создания страницы
            
        Returns:
            DTO созданной страницы
            
        Raises:
            PageSlugAlreadyExists: Если slug уже существует
        """
        try:
            async with self._uow:
                # Проверяем уникальность slug через Domain Service
                await self._slug_uniqueness_service.ensure_slug_is_unique(dto.slug)

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
                            block_type=block_dto.block_type,
                            data=block_dto.data or {},
                            order=block_dto.order,
                        )

                # Сохраняем
                await self._repository.create(aggregate)

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
