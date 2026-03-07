from src.cms.domain.repository.feature_flag import FeatureFlagRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class DeleteFeatureFlagCommand:
    """Command для удаления feature flag."""

    def __init__(
        self,
        repository: FeatureFlagRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, flag_id: int) -> bool:
        aggregate = await self.repository.get_by_id(flag_id)
        if not aggregate:
            from src.cms.domain.exceptions import FeatureFlagNotFound
            raise FeatureFlagNotFound()

        try:
            async with self.uow:
                result = await self.repository.delete(flag_id)

            if result:
                self.event_bus.publish_many_nowait([build_event(
                    event_type="crud",
                    method="delete",
                    app="cms",
                    entity="feature_flag",
                    entity_id=flag_id,
                    data={"flag_id": flag_id},
                )])

            return result

        except Exception:
            raise
