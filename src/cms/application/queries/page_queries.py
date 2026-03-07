from typing import Optional

from sqlalchemy import select
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
        """Получить страницу по slug."""
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
