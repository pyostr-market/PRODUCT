from typing import Any

from src.catalog.product.domain.aggregates.tag import TagDeletedEvent
from src.catalog.product.domain.exceptions import TagNotFound
from src.catalog.product.domain.repository.tag import TagRepositoryInterface
from src.core.auth.schemas.user import User
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class DeleteTagCommand:
    """Команда для удаления тега."""

    def __init__(
        self,
        repository: TagRepositoryInterface,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, tag_id: int, user: User) -> None:
        """Выполнить команду."""
        tag = await self.repository.get(tag_id)
        if not tag:
            raise TagNotFound(details={"tag_id": tag_id})

        tag_name = tag.name
        domain_events = tag.get_events()

        async with self.uow:
            await self.repository.delete(tag_id)

        # Публикуем события
        events = self._build_domain_events(tag_id, tag_name)
        if events:
            self.event_bus.publish_many_nowait(events)

    def _build_domain_events(
        self,
        tag_id: int,
        tag_name: str,
    ) -> list[dict[str, Any]]:
        """Построить события для публикации."""
        return [
            build_event(
                event_type="crud",
                method="delete",
                app="products",
                entity="tag",
                entity_id=tag_id,
                data={
                    "tag_id": tag_id,
                    "name": tag_name,
                },
            )
        ]
