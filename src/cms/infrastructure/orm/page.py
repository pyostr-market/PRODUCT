from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.cms.domain.aggregates.page import PageAggregate
from src.cms.domain.aggregates.page_block import PageBlockAggregate
from src.cms.domain.repository.page import PageRepository
from src.cms.domain.value_objects.page_block_data import PageBlockData
from src.cms.infrastructure.models.page import CmsPage
from src.cms.infrastructure.models.page_block import CmsPageBlock


class SqlAlchemyPageRepository(PageRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, page_id: int) -> Optional[PageAggregate]:
        stmt = (
            select(CmsPage)
            .options(selectinload(CmsPage.blocks))
            .where(CmsPage.id == page_id)
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def get_by_slug(self, slug: str) -> Optional[PageAggregate]:
        stmt = (
            select(CmsPage)
            .options(selectinload(CmsPage.blocks))
            .where(CmsPage.slug == slug)
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def create(self, aggregate: PageAggregate) -> PageAggregate:
        model = CmsPage(
            slug=aggregate.slug,
            title=aggregate.title,
            is_published=aggregate.is_published,
        )

        self.db.add(model)
        await self.db.flush()

        # Добавляем блоки
        for idx, block in enumerate(aggregate.blocks):
            block_model = CmsPageBlock(
                page_id=model.id,
                block_type=block.block_type,
                order=block.order,
                data=block.data.data,
                is_active=block.is_active,
            )
            self.db.add(block_model)

        await self.db.flush()

        # Устанавливаем ID для агрегата и блоков
        aggregate._set_id(model.id)
        
        # Обновляем ID блоков из модели БД
        stmt = (
            select(CmsPageBlock)
            .where(CmsPageBlock.page_id == model.id)
            .order_by(CmsPageBlock.id)
        )
        result = await self.db.execute(stmt)
        block_models = result.scalars().all()
        
        # Сопоставляем блоки агрегата с моделями БД по порядку
        for agg_block, db_block in zip(aggregate.blocks, block_models):
            agg_block._set_id(db_block.id)
        
        return aggregate

    async def delete(self, page_id: int) -> bool:
        model = await self.db.get(CmsPage, page_id)
        if not model:
            return False

        await self.db.delete(model)
        return True

    async def update(self, aggregate: PageAggregate) -> PageAggregate:
        model = await self.db.get(CmsPage, aggregate.id)
        if not model:
            raise ValueError(f"Page with id {aggregate.id} not found")

        model.slug = aggregate.slug
        model.title = aggregate.title
        model.is_published = aggregate.is_published

        # Удаляем старые блоки
        stmt = select(CmsPageBlock).where(CmsPageBlock.page_id == aggregate.id)
        result = await self.db.execute(stmt)
        for block_model in result.scalars().all():
            await self.db.delete(block_model)

        # Создаём новые блоки
        for block in aggregate.blocks:
            self.db.add(
                CmsPageBlock(
                    page_id=aggregate.id,
                    block_type=block.block_type,
                    order=block.order,
                    data=block.data.data,
                    is_active=block.is_active,
                )
            )

        await self.db.flush()
        return aggregate

    async def exists_by_slug(self, slug: str, exclude_id: Optional[int] = None) -> bool:
        stmt = select(CmsPage.id).where(CmsPage.slug == slug)
        if exclude_id:
            stmt = stmt.where(CmsPage.id != exclude_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _to_aggregate(self, model: CmsPage) -> PageAggregate:
        blocks = [
            PageBlockAggregate(
                block_id=block.id,
                page_id=model.id,
                block_type=block.block_type,
                order=block.order,
                data=block.data,
                is_active=block.is_active,
            )
            for block in sorted(model.blocks, key=lambda b: b.order)
        ]

        return PageAggregate(
            page_id=model.id,
            slug=model.slug,
            title=model.title,
            is_published=model.is_published,
            blocks=blocks,
        )
