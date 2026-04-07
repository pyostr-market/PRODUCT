from typing import List, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.product.application.dto.product import ProductTagReadDTO, TagReadDTO
from src.catalog.product.domain.repository.product_tag_read import ProductTagReadRepositoryInterface
from src.catalog.product.infrastructure.models.product_tag import ProductTag
from src.catalog.product.infrastructure.models.tag import Tag


class SqlAlchemyProductTagReadRepository(ProductTagReadRepositoryInterface):
    """SQLAlchemy реализация read-репозитория для связей товаров с тегами."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_product(
        self,
        product_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> Tuple[List[ProductTagReadDTO], int]:
        """Получить все связи для товара с информацией о тегах."""
        # Считаем общее количество
        count_stmt = select(func.count(ProductTag.id)).where(
            ProductTag.product_id == product_id
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar_one()

        # Получаем связи с тегами
        stmt = (
            select(ProductTag)
            .options(selectinload(ProductTag.tag))
            .where(ProductTag.product_id == product_id)
            .order_by(ProductTag.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        product_tags = result.scalars().all()

        dtos = [
            ProductTagReadDTO(
                id=pt.id,
                product_id=pt.product_id,
                tag_id=pt.tag_id,
                tag=TagReadDTO(
                    tag_id=pt.tag.id,
                    name=pt.tag.name,
                    description=pt.tag.description,
                ),
            )
            for pt in product_tags
        ]

        return dtos, total
