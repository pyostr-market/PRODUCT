from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.domain.aggregates.feature_flag import FeatureFlagAggregate
from src.cms.domain.repository.feature_flag import FeatureFlagRepository
from src.cms.infrastructure.models.feature_flag import CmsFeatureFlag


class SqlAlchemyFeatureFlagRepository(FeatureFlagRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, flag_id: int) -> Optional[FeatureFlagAggregate]:
        model = await self.db.get(CmsFeatureFlag, flag_id)
        if not model:
            return None

        return self._to_aggregate(model)

    async def get_by_key(self, key: str) -> Optional[FeatureFlagAggregate]:
        stmt = select(CmsFeatureFlag).where(CmsFeatureFlag.key == key)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def get_all(self) -> list[FeatureFlagAggregate]:
        stmt = select(CmsFeatureFlag).order_by(CmsFeatureFlag.key)
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_aggregate(model) for model in models]

    async def create(self, aggregate: FeatureFlagAggregate) -> FeatureFlagAggregate:
        model = CmsFeatureFlag(
            key=aggregate.key,
            enabled=aggregate.enabled,
            description=aggregate.description,
        )

        self.db.add(model)
        await self.db.flush()

        aggregate._set_id(model.id)
        return aggregate

    async def delete(self, flag_id: int) -> bool:
        model = await self.db.get(CmsFeatureFlag, flag_id)
        if not model:
            return False

        await self.db.delete(model)
        return True

    async def update(self, aggregate: FeatureFlagAggregate) -> FeatureFlagAggregate:
        model = await self.db.get(CmsFeatureFlag, aggregate.id)
        if not model:
            raise ValueError(f"Feature flag with id {aggregate.id} not found")

        model.key = aggregate.key
        model.enabled = aggregate.enabled
        model.description = aggregate.description

        await self.db.flush()
        return aggregate

    def _to_aggregate(self, model: CmsFeatureFlag) -> FeatureFlagAggregate:
        return FeatureFlagAggregate(
            flag_id=model.id,
            key=model.key,
            enabled=model.enabled,
            description=model.description,
        )
