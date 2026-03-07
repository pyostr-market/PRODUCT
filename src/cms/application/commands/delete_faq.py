from src.cms.domain.repository.faq import FaqRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class DeleteFaqCommand:
    """Command для удаления FAQ."""

    def __init__(
        self,
        repository: FaqRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, faq_id: int) -> bool:
        aggregate = await self.repository.get_by_id(faq_id)
        if not aggregate:
            from src.cms.domain.exceptions import FaqNotFound
            raise FaqNotFound(faq_id)

        try:
            async with self.uow:
                result = await self.repository.delete(faq_id)

            if result:
                self.event_bus.publish_many_nowait([build_event(
                    event_type="crud",
                    method="delete",
                    app="cms",
                    entity="faq",
                    entity_id=faq_id,
                    data={"faq_id": faq_id},
                )])

            return result

        except Exception:
            raise
