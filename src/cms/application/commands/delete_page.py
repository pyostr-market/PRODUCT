from src.cms.domain.repository.page import PageRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class DeletePageCommand:
    """Command для удаления страницы."""

    def __init__(
        self,
        repository: PageRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, page_id: int) -> bool:
        # Проверяем существование
        aggregate = await self.repository.get_by_id(page_id)
        if not aggregate:
            from src.cms.domain.exceptions import PageNotFound
            raise PageNotFound()

        try:
            async with self.uow:
                # Удаляем
                result = await self.repository.delete(page_id)

            if result:
                # Публикуем событие
                self.event_bus.publish_many_nowait([build_event(
                    event_type="crud",
                    method="delete",
                    app="cms",
                    entity="page",
                    entity_id=page_id,
                    data={"page_id": page_id},
                )])

            return result

        except Exception:
            raise
