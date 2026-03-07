from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.application.dto.cms_dto import SeoReadDTO
from src.cms.infrastructure.models.seo import CmsSeo


class SeoQueries:
    """Query класс для получения SEO данных."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_page_slug(self, page_slug: str) -> Optional[SeoReadDTO]:
        """Получить SEO по slug страницы."""
        stmt = select(CmsSeo).where(CmsSeo.page_slug == page_slug)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    def _to_read_dto(self, model: CmsSeo) -> SeoReadDTO:
        return SeoReadDTO(
            id=model.id,
            page_slug=model.page_slug,
            title=model.title,
            description=model.description,
            keywords=model.keywords or [],
            og_image_id=model.og_image_id,
        )
