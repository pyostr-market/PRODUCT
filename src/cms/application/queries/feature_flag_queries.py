from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.application.dto.cms_dto import FeatureFlagReadDTO
from src.cms.infrastructure.models.feature_flag import CmsFeatureFlag


class FeatureFlagQueries:
    """Query класс для получения feature flags."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_key(self, key: str) -> Optional[FeatureFlagReadDTO]:
        """Получить flag по ключу."""
        stmt = select(CmsFeatureFlag).where(CmsFeatureFlag.key == key)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def get_all(self) -> list[FeatureFlagReadDTO]:
        """Получить все flags."""
        stmt = select(CmsFeatureFlag).order_by(CmsFeatureFlag.key)
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models]

    async def get_enabled(self) -> list[str]:
        """Получить ключи всех включенных flags."""
        stmt = select(CmsFeatureFlag.key).where(CmsFeatureFlag.enabled == True)
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all()]

    def _to_read_dto(self, model: CmsFeatureFlag) -> FeatureFlagReadDTO:
        return FeatureFlagReadDTO(
            id=model.id,
            key=model.key,
            enabled=model.enabled,
            description=model.description,
        )
