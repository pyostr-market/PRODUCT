from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.application.dto.cms_dto import FeatureFlagReadDTO
from src.cms.infrastructure.models.feature_flag import CmsFeatureFlag


class FeatureFlagQueries:
    """Query класс для получения feature flags."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, flag_id: int) -> Optional[FeatureFlagReadDTO]:
        """Получить flag по ID."""
        stmt = select(CmsFeatureFlag).where(CmsFeatureFlag.id == flag_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def get_by_key(self, key: str) -> Optional[FeatureFlagReadDTO]:
        """Получить flag по ключу."""
        stmt = select(CmsFeatureFlag).where(CmsFeatureFlag.key == key)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def filter(
        self,
        enabled: Optional[bool] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list[FeatureFlagReadDTO], int]:
        """
        Фильтрация feature flags с пагинацией.

        Args:
            enabled: Фильтр по статусу
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Кортеж из списка DTO и общего количества записей
        """
        stmt = select(CmsFeatureFlag)

        if enabled is not None:
            stmt = stmt.where(CmsFeatureFlag.enabled == enabled)

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsFeatureFlag.key).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list[FeatureFlagReadDTO], int]:
        """
        Поиск feature flags по key и description (LIKE).

        Args:
            query: Поисковый запрос
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Кортеж из списка DTO и общего количества записей
        """
        stmt = select(CmsFeatureFlag)

        if query:
            stmt = stmt.where(
                (CmsFeatureFlag.key.ilike(f"%{query}%")) |
                (CmsFeatureFlag.description.ilike(f"%{query}%"))
            )

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsFeatureFlag.key).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

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
