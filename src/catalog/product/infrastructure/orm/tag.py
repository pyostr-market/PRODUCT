from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.domain.aggregates.tag import TagAggregate
from src.catalog.product.domain.repository.tag import TagRepositoryInterface
from src.catalog.product.infrastructure.models.tag import Tag


class SqlAlchemyTagRepository(TagRepositoryInterface):
    """SQLAlchemy реализация репозитория для тегов."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_aggregate(self, model: Tag) -> TagAggregate:
        """Преобразовать модель в агрегат."""
        return TagAggregate(
            _tag_id=model.id,
            _name=model.name,
            _description=model.description,
            _color=model.color,
        )

    async def get(self, tag_id: int) -> Optional[TagAggregate]:
        """Получить тег по ID."""
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_aggregate(model)

    async def get_by_name(self, name: str) -> Optional[TagAggregate]:
        """Получить тег по имени."""
        stmt = select(Tag).where(Tag.name == name)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_aggregate(model)

    async def create(self, aggregate: TagAggregate) -> TagAggregate:
        """Создать новый тег."""
        db_tag = Tag(
            name=aggregate.name,
            description=aggregate.description,
            color=aggregate.color,
        )
        self.db.add(db_tag)
        await self.db.flush()
        await self.db.refresh(db_tag)

        aggregate._set_id(db_tag.id)
        return aggregate

    async def update(self, aggregate: TagAggregate) -> TagAggregate:
        """Обновить тег."""
        stmt = select(Tag).where(Tag.id == aggregate.tag_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        model.name = aggregate.name
        model.description = aggregate.description
        model.color = aggregate.color
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_aggregate(model)

    async def delete(self, tag_id: int) -> bool:
        """Удалить тег."""
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.db.delete(model)
        await self.db.flush()
        return True

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[TagAggregate]:
        """Получить все теги с пагинацией."""
        stmt = select(Tag).order_by(Tag.id).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._to_aggregate(model) for model in models]

    async def count(self) -> int:
        """Получить общее количество тегов."""
        stmt = select(func.count(Tag.id))
        result = await self.db.execute(stmt)
        return result.scalar_one()
