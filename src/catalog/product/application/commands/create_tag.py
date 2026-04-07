from typing import Any

from src.catalog.product.application.dto.product import TagCreateDTO, TagReadDTO
from src.catalog.product.domain.aggregates.tag import TagAggregate, TagCreatedEvent
from src.catalog.product.domain.exceptions import TagAlreadyExists
from src.catalog.product.domain.repository.tag import TagRepositoryInterface
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class CreateTagCommand:
    """Команда для создания тега."""

    def __init__(
        self,
        repository: TagRepositoryInterface,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, dto: TagCreateDTO, user: User) -> TagReadDTO:
        """Выполнить команду."""
        # Проверяем, что тег с таким именем не существует
        existing = await self.repository.get_by_name(dto.name)
        if existing:
            raise TagAlreadyExists(details={"name": dto.name})

        async with self.uow:
            aggregate = TagAggregate(
                _name=dto.name,
                _description=dto.description,
            )

            await self.repository.create(aggregate)

            # Получаем доменные события
            domain_events = aggregate.get_events()

            result = self._to_read_dto(aggregate)

        # Публикуем события
        events = self._build_domain_events(aggregate, domain_events)
        if events:
            self.event_bus.publish_many_nowait(events)

        return result

    def _build_domain_events(
        self,
        aggregate: TagAggregate,
        domain_events: list,
    ) -> list[dict[str, Any]]:
        """Преобразовать доменные события в события для публикации."""
        events: list[dict[str, Any]] = []

        for event in domain_events:
            if isinstance(event, TagCreatedEvent):
                events.append(
                    build_event(
                        event_type="crud",
                        method="create",
                        app="products",
                        entity="tag",
                        entity_id=aggregate.tag_id,
                        data={
                            "tag_id": aggregate.tag_id,
                            "name": aggregate.name,
                            "description": aggregate.description,
                        },
                    )
                )

        return events

    def _to_read_dto(self, aggregate: TagAggregate) -> TagReadDTO:
        """Преобразовать агрегат в DTO для чтения."""
        return TagReadDTO(
            tag_id=aggregate.tag_id,
            name=aggregate.name,
            description=aggregate.description,
        )
