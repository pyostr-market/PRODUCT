from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.product.application.dto.product import TagReadDTO
from src.catalog.product.infrastructure.models.product_tag import ProductTag
from src.catalog.product.infrastructure.models.tag import Tag


class TagQueries:
    """Queries для получения тегов."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tag_by_id(self, tag_id: int) -> Optional[TagReadDTO]:
        """Получить тег по ID."""
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await self.db.execute(stmt)
        tag = result.scalar_one_or_none()
        if not tag:
            return None
        return TagReadDTO(
            tag_id=tag.id,
            name=tag.name,
            description=tag.description,
        )

    async def get_all_tags(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[TagReadDTO], int]:
        """Получить все теги с пагинацией."""
        # Получаем общее количество
        count_stmt = select(func.count(Tag.id))
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        # Получаем теги с пагинацией
        stmt = select(Tag).order_by(Tag.id).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        tags = result.scalars().all()

        return [
            TagReadDTO(
                tag_id=tag.id,
                name=tag.name,
                description=tag.description,
            )
            for tag in tags
        ], total

    async def get_product_tags(
        self,
        product_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[TagReadDTO], int]:
        """Получить все теги товара."""
        # Получаем общее количество
        count_stmt = select(func.count(ProductTag.id)).where(
            ProductTag.product_id == product_id
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        # Получаем теги с пагинацией
        stmt = (
            select(Tag)
            .join(ProductTag, ProductTag.tag_id == Tag.id)
            .where(ProductTag.product_id == product_id)
            .order_by(Tag.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        tags = result.scalars().all()

        return [
            TagReadDTO(
                tag_id=tag.id,
                name=tag.name,
                description=tag.description,
            )
            for tag in tags
        ], total
