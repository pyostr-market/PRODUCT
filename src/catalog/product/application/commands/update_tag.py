from typing import Any

from src.catalog.product.application.dto.product import TagReadDTO, TagUpdateDTO
from src.catalog.product.domain.aggregates.tag import TagUpdatedEvent
from src.catalog.product.domain.exceptions import TagAlreadyExists, TagNotFound
from src.catalog.product.domain.repository.tag import TagRepositoryInterface
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class UpdateTagCommand:
    """Команда для обновления тега."""

    def __init__(
        self,
        repository: TagRepositoryInterface,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, tag_id: int, dto: TagUpdateDTO, user: User) -> TagReadDTO:
        """Выполнить команду."""
        tag = await self.repository.get(tag_id)
        if not tag:
            raise TagNotFound(details={"tag_id": tag_id})

        # Проверяем уникальность имени, если оно меняется
        if dto.name and dto.name != tag.name:
            existing = await self.repository.get_by_name(dto.name)
            if existing:
                raise TagAlreadyExists(details={"name": dto.name})

        old_name = tag.name
        old_description = tag.description

        async with self.uow:
            tag.update(name=dto.name, description=dto.description)

            updated = await self.repository.update(tag)

            # Получаем доменные события
            domain_events = tag.get_events()

            result = self._to_read_dto(updated)

        # Публикуем события
        events = self._build_domain_events(tag, domain_events, old_name, old_description)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _build_domain_events(
        self,
        aggregate,
        domain_events: list,
        old_name: str,
        old_description: str | None,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, TagUpdatedEvent):
                events.append(
                    build_event(
                        event_type="crud",
                        method="update",
                        app="products",
                        entity="tag",
                        entity_id=aggregate.tag_id,
                        data={
                            "tag_id": aggregate.tag_id,
                            "old_name": old_name,
                            "new_name": aggregate.name,
                            "old_description": old_description,
                            "new_description": aggregate.description,
                        },
                    )
                )

        return events

    def _to_read_dto(self, aggregate) -> TagReadDTO:
        """Преобразовать агрегат в DTO для чтения."""
        return TagReadDTO(
            tag_id=aggregate.tag_id,
            name=aggregate.name,
            description=aggregate.description,
        )
