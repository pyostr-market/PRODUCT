from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.domain.aggregates.product_tag import ProductTagAggregate
from src.catalog.product.domain.repository.product_tag import ProductTagRepositoryInterface
from src.catalog.product.infrastructure.models.product_tag import ProductTag


class SqlAlchemyProductTagRepository(ProductTagRepositoryInterface):
    """SQLAlchemy реализация репозитория для связей товаров с тегами."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_aggregate(self, model: ProductTag) -> ProductTagAggregate:
        """Преобразовать модель в агрегат."""
        return ProductTagAggregate(
            _id=model.id,
            _product_id=model.product_id,
            _tag_id=model.tag_id,
        )

    async def get(self, link_id: int) -> Optional[ProductTagAggregate]:
        """Получить связь по ID."""
        stmt = select(ProductTag).where(ProductTag.id == link_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_aggregate(model)

    async def get_by_product(
        self,
        product_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ProductTagAggregate]:
        """Получить все связи для товара."""
        stmt = (
            select(ProductTag)
            .where(ProductTag.product_id == product_id)
            .order_by(ProductTag.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._to_aggregate(model) for model in models]

    async def exists(self, product_id: int, tag_id: int) -> bool:
        """Проверить существование связи."""
        stmt = select(ProductTag).where(
            ProductTag.product_id == product_id,
            ProductTag.tag_id == tag_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, aggregate: ProductTagAggregate) -> ProductTagAggregate:
        """Создать связь."""
        db_link = ProductTag(
            product_id=aggregate.product_id,
            tag_id=aggregate.tag_id,
        )
        self.db.add(db_link)
        await self.db.flush()
        await self.db.refresh(db_link)

        aggregate._set_id(db_link.id)
        return aggregate

    async def delete(self, product_id: int, tag_id: int) -> bool:
        """Удалить связь по product_id и tag_id."""
        stmt = select(ProductTag).where(
            ProductTag.product_id == product_id,
            ProductTag.tag_id == tag_id,
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.db.delete(model)
        await self.db.flush()
        return True

    async def count_by_product(self, product_id: int) -> int:
        """Получить количество тегов у товара."""
        stmt = select(func.count(ProductTag.id)).where(
            ProductTag.product_id == product_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
