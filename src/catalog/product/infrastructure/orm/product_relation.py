from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.domain.aggregates.product_relation import (
    ProductRelationAggregate,
    ProductRelationCreatedEvent,
    ProductRelationDeletedEvent,
    ProductRelationUpdatedEvent,
)
from src.catalog.product.domain.exceptions import (
    ProductRelationNotFound,
    ProductRelationSelfReference,
)
from src.catalog.product.domain.repository.product_relation import ProductRelationRepository
from src.catalog.product.infrastructure.models.product_relation import ProductRelation


class SqlAlchemyProductRelationRepository(ProductRelationRepository):
    """SQLAlchemy реализация репозитория связей товаров."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, relation_id: int) -> Optional[ProductRelationAggregate]:
        """Получить связь по ID."""
        model = await self.db.get(ProductRelation, relation_id)

        if not model:
            return None

        return self._to_aggregate(model)

    async def get_by_product(
        self,
        product_id: int,
        relation_type: Optional[str] = None,
    ) -> List[ProductRelationAggregate]:
        """Получить все связи для товара (опционально по типу)."""
        stmt = select(ProductRelation).where(ProductRelation.product_id == product_id)

        if relation_type:
            stmt = stmt.where(ProductRelation.relation_type == relation_type)

        stmt = stmt.order_by(ProductRelation.sort_order, ProductRelation.id)

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_aggregate(model) for model in models]

    async def exists(
        self,
        product_id: int,
        related_product_id: int,
        relation_type: str,
    ) -> bool:
        """Проверить существование связи."""
        stmt = select(ProductRelation.id).where(
            ProductRelation.product_id == product_id,
            ProductRelation.related_product_id == related_product_id,
            ProductRelation.relation_type == relation_type,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create(self, aggregate: ProductRelationAggregate) -> ProductRelationAggregate:
        """Создать связь."""
        model = ProductRelation(
            product_id=aggregate.product_id,
            related_product_id=aggregate.related_product_id,
            relation_type=aggregate.relation_type,
            sort_order=aggregate.sort_order,
        )
        self.db.add(model)
        await self.db.flush()

        aggregate._set_id(model.id)
        
        # Записываем событие создания
        aggregate._record_event(ProductRelationCreatedEvent(
            relation_id=model.id,
            product_id=aggregate.product_id,
            related_product_id=aggregate.related_product_id,
            relation_type=aggregate.relation_type,
            sort_order=aggregate.sort_order,
        ))
        
        return aggregate

    async def update(self, aggregate: ProductRelationAggregate) -> ProductRelationAggregate:
        """Обновить связь."""
        model = await self.db.get(ProductRelation, aggregate.id)

        if not model:
            raise ProductRelationNotFound()

        if aggregate.relation_type is not None:
            model.relation_type = aggregate.relation_type

        if aggregate.sort_order is not None:
            model.sort_order = aggregate.sort_order

        await self.db.flush()
        
        # Записываем событие обновления
        aggregate._record_event(ProductRelationUpdatedEvent(
            relation_id=model.id,
            changed_fields={
                k: v for k, v in [
                    ("relation_type", aggregate.relation_type) if aggregate.relation_type is not None else None,
                    ("sort_order", aggregate.sort_order) if aggregate.sort_order is not None else None,
                ] if v is not None
            },
        ))
        
        return aggregate

    async def delete(self, relation_id: int) -> bool:
        """Удалить связь по ID."""
        model = await self.db.get(ProductRelation, relation_id)

        if not model:
            return False

        # Записываем событие удаления перед удалением модели
        aggregate = self._to_aggregate(model)
        aggregate._record_event(ProductRelationDeletedEvent(
            relation_id=model.id,
        ))

        await self.db.delete(model)
        return True

    @staticmethod
    def _to_aggregate(model: ProductRelation) -> ProductRelationAggregate:
        """Конвертировать ORM модель в агрегат."""
        return ProductRelationAggregate(
            relation_id=model.id,
            product_id=model.product_id,
            related_product_id=model.related_product_id,
            relation_type=model.relation_type,
            sort_order=model.sort_order,
        )
