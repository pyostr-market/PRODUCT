from src.cms.domain.repository.seo import SeoRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class DeleteSeoCommand:
    """Command для удаления SEO данных."""

    def __init__(
        self,
        repository: SeoRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, seo_id: int) -> bool:
        aggregate = await self.repository.get_by_id(seo_id)
        if not aggregate:
            from src.cms.domain.exceptions import SeoNotFound
            raise SeoNotFound()

        try:
            async with self.uow:
                result = await self.repository.delete(seo_id)

            if result:
                self.event_bus.publish_many_nowait([build_event(
                    event_type="crud",
                    method="delete",
                    app="cms",
                    entity="seo",
                    entity_id=seo_id,
                    data={"seo_id": seo_id},
                )])

            return result

        except Exception:
            raise
