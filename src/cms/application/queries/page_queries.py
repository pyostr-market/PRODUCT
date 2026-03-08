from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.cms.application.dto.cms_dto import PageBlockReadDTO, PageReadDTO
from src.cms.infrastructure.models.page import CmsPage
from src.cms.infrastructure.models.page_block import CmsPageBlock


class PageQueries:
    """Query класс для получения страниц."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_slug(self, slug: str) -> Optional[PageReadDTO]:
        """Получить страницу по slug (только опубликованные)."""
        stmt = (
            select(CmsPage)
            .options(selectinload(CmsPage.blocks))
            .where(CmsPage.slug == slug)
            .where(CmsPage.is_published == True)
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def get_by_id(self, page_id: int) -> Optional[PageReadDTO]:
        """Получить страницу по ID."""
        stmt = (
            select(CmsPage)
            .options(selectinload(CmsPage.blocks))
            .where(CmsPage.id == page_id)
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def get_all_published(self) -> list[PageReadDTO]:
        """Получить все опубликованные страницы."""
        stmt = (
            select(CmsPage)
            .options(selectinload(CmsPage.blocks))
            .where(CmsPage.is_published == True)
            .order_by(CmsPage.title)
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models]

    async def filter(
        self,
        title: Optional[str] = None,
        is_published: Optional[bool] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list[PageReadDTO], int]:
        """
        Фильтрация страниц с пагинацией.

        Args:
            title: Фильтр по заголовку (частичное совпадение)
            is_published: Фильтр по статусу публикации
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Кортеж из списка DTO и общего количества записей
        """
        stmt = select(CmsPage).options(selectinload(CmsPage.blocks))

        if title:
            stmt = stmt.where(CmsPage.title.ilike(f"%{title}%"))

        if is_published is not None:
            stmt = stmt.where(CmsPage.is_published == is_published)

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsPage.id).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

    async def search(self, query: str, limit: int = 10, offset: int = 0) -> Tuple[list[PageReadDTO], int]:
        """
        Поиск страниц по заголовку (LIKE).

        Args:
            query: Поисковый запрос
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Кортеж из списка DTO и общего количества записей
        """
        stmt = select(CmsPage).options(selectinload(CmsPage.blocks))

        if query:
            stmt = stmt.where(CmsPage.title.ilike(f"%{query}%"))

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsPage.id).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

    def _to_read_dto(self, model: CmsPage) -> PageReadDTO:
        return PageReadDTO(
            id=model.id,
            slug=model.slug,
            title=model.title,
            is_published=model.is_published,
            blocks=[
                PageBlockReadDTO(
                    id=block.id,
                    page_id=block.page_id,
                    block_type=block.block_type,
                    order=block.order,
                    data=block.data,
                    is_active=block.is_active,
                )
                for block in sorted(model.blocks, key=lambda b: b.order)
                if block.is_active
            ],
        )
