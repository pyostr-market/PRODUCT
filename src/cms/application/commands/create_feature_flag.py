from src.cms.application.dto.cms_dto import FeatureFlagCreateDTO, FeatureFlagReadDTO
from src.cms.domain.aggregates.feature_flag import FeatureFlagAggregate
from src.cms.domain.exceptions import FeatureFlagKeyAlreadyExists
from src.cms.domain.repository.feature_flag import FeatureFlagRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.events import AsyncEventBus, build_event


class CreateFeatureFlagCommand:
    """Command для создания feature flag."""

    def __init__(
        self,
        repository: FeatureFlagRepository,
        uow: UnitOfWork,
        event_bus: AsyncEventBus,
    ):
        self.repository = repository
        self.uow = uow
        self.event_bus = event_bus

    async def execute(self, dto: FeatureFlagCreateDTO) -> FeatureFlagReadDTO:
        # Проверяем уникальность ключа
        existing = await self.repository.get_by_key(dto.key)
        if existing:
            raise FeatureFlagKeyAlreadyExists(dto.key)

        aggregate = FeatureFlagAggregate(
            flag_id=None,
            key=dto.key,
            enabled=dto.enabled,
            description=dto.description,
        )

        try:
            async with self.uow:
                await self.repository.create(aggregate)

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
