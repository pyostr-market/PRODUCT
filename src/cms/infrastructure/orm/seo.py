from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.domain.aggregates.seo import SeoAggregate
from src.cms.domain.repository.seo import SeoRepository
from src.cms.infrastructure.models.seo import CmsSeo


class SqlAlchemySeoRepository(SeoRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, seo_id: int) -> Optional[SeoAggregate]:
        model = await self.db.get(CmsSeo, seo_id)
        if not model:
            return None

        return self._to_aggregate(model)

    async def get_by_page_slug(self, page_slug: str) -> Optional[SeoAggregate]:
        stmt = select(CmsSeo).where(CmsSeo.page_slug == page_slug)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def create(self, aggregate: SeoAggregate) -> SeoAggregate:
        model = CmsSeo(
            page_slug=aggregate.page_slug,
            title=aggregate.title,
            description=aggregate.description,
            keywords=aggregate.keywords,
            og_image_id=aggregate.og_image_id,
        )

        self.db.add(model)
        await self.db.flush()

        aggregate._set_id(model.id)
        return aggregate

    async def delete(self, seo_id: int) -> bool:
        model = await self.db.get(CmsSeo, seo_id)
        if not model:
            return False

        await self.db.delete(model)
        return True

    async def update(self, aggregate: SeoAggregate) -> SeoAggregate:
        model = await self.db.get(CmsSeo, aggregate.id)
        if not model:
            raise ValueError(f"SEO with id {aggregate.id} not found")

        model.page_slug = aggregate.page_slug
        model.title = aggregate.title
        model.description = aggregate.description
        model.keywords = aggregate.keywords
        model.og_image_id = aggregate.og_image_id

        await self.db.flush()
        return aggregate

    def _to_aggregate(self, model: CmsSeo) -> SeoAggregate:
        return SeoAggregate(
            seo_id=model.id,
            page_slug=model.page_slug,
            title=model.title,
            description=model.description,
            keywords=model.keywords or [],
            og_image_id=model.og_image_id,
        )
