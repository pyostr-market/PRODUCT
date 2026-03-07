from src.cms.application.dto.cms_dto import FeatureFlagReadDTO, FeatureFlagUpdateDTO
from src.cms.domain.repository.feature_flag import FeatureFlagRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class UpdateFeatureFlagCommand:
    """Command для обновления feature flag."""

    def __init__(
        self,
        repository: FeatureFlagRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(
        self,
        flag_id: int,
        dto: FeatureFlagUpdateDTO,
    ) -> FeatureFlagReadDTO:
        aggregate = await self.repository.get_by_id(flag_id)
        if not aggregate:
            from src.cms.domain.exceptions import FeatureFlagNotFound
            raise FeatureFlagNotFound()

        try:
            async with self.uow:
                if dto.enabled is not None:
                    if dto.enabled:
                        aggregate.enable()
                    else:
                        aggregate.disable()

                if dto.description is not None:
                    aggregate.update_description(dto.description)

                await self.repository.update(aggregate)
                domain_events = aggregate.get_events()

            # Публикуем события
            if domain_events:
                self.event_bus.publish_many_nowait([build_event(
                    event_type="crud",
                    method="update",
                    app="cms",
                    entity="feature_flag",
                    entity_id=aggregate.id,
                    data={
                        "flag_id": aggregate.id,
                        "key": aggregate.key,
                        "enabled": aggregate.enabled,
                    },
                )])

            return self._to_read_dto(aggregate)

        except Exception:
            raise

    def _to_read_dto(self, aggregate) -> FeatureFlagReadDTO:
        return FeatureFlagReadDTO(
            id=aggregate.id,
            key=aggregate.key,
            enabled=aggregate.enabled,
            description=aggregate.description,
        )
