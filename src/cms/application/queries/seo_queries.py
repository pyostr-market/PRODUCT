from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.application.dto.cms_dto import SeoReadDTO
from src.cms.infrastructure.models.seo import CmsSeo


class SeoQueries:
    """Query класс для получения SEO данных."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, seo_id: int) -> Optional[SeoReadDTO]:
        """Получить SEO данные по ID."""
        stmt = select(CmsSeo).where(CmsSeo.id == seo_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def get_by_page_slug(self, page_slug: str) -> Optional[SeoReadDTO]:
        """Получить SEO по slug страницы."""
        stmt = select(CmsSeo).where(CmsSeo.page_slug == page_slug)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def filter(
        self,
        page_slug: Optional[str] = None,
        title: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list[SeoReadDTO], int]:
        """
        Фильтрация SEO данных с пагинацией.

        Args:
            page_slug: Фильтр по slug страницы
            title: Фильтр по заголовку (частичное совпадение)
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Кортеж из списка DTO и общего количества записей
        """
        stmt = select(CmsSeo)

        if page_slug:
            stmt = stmt.where(CmsSeo.page_slug == page_slug)

        if title:
            stmt = stmt.where(CmsSeo.title.ilike(f"%{title}%"))

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsSeo.id).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list[SeoReadDTO], int]:
        """
        Поиск SEO данных по title и description (LIKE).

        Args:
            query: Поисковый запрос
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Кортеж из списка DTO и общего количества записей
        """
        stmt = select(CmsSeo)

        if query:
            stmt = stmt.where(
                (CmsSeo.title.ilike(f"%{query}%")) | (CmsSeo.description.ilike(f"%{query}%"))
            )

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsSeo.id).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

    def _to_read_dto(self, model: CmsSeo) -> SeoReadDTO:
        return SeoReadDTO(
            id=model.id,
            page_slug=model.page_slug,
            title=model.title,
            description=model.description,
            keywords=model.keywords or [],
            og_image_id=model.og_image_id,
        )
