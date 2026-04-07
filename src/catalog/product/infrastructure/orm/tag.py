from typing import List, Optional

from sqlalchemy import select
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
            tag_id=model.id,
            name=model.name,
            description=model.description,
        )

    async def create(self, tag: TagAggregate) -> TagAggregate:
        """Создать новый тег."""
        db_tag = Tag(
            name=tag.name,
            description=tag.description,
        )
        self.db.add(db_tag)
        await self.db.flush()
        await self.db.refresh(db_tag)
        return self._to_aggregate(db_tag)

    async def get_by_id(self, tag_id: int) -> Optional[TagAggregate]:
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

    async def update(self, tag: TagAggregate) -> TagAggregate:
        """Обновить тег."""
        stmt = select(Tag).where(Tag.id == tag.tag_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Tag with id {tag.tag_id} not found")

        model.name = tag.name
        model.description = tag.description
        await self.db.flush()
        await self.db.refresh(model)
        return self._to_aggregate(model)

    async def delete(self, tag_id: int) -> None:
        """Удалить тег."""
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Tag with id {tag_id} not found")
        await self.db.delete(model)
        await self.db.flush()

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[TagAggregate]:
        """Получить все теги с пагинацией."""
        stmt = select(Tag).order_by(Tag.id).offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._to_aggregate(model) for model in models]
