from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.category.application.dto.category import (
    CategoryImageReadDTO,
    CategoryReadDTO,
)
from src.catalog.category.infrastructure.models.categories import Category


class CategoryReadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: int) -> Optional[CategoryReadDTO]:
        stmt = (
            select(Category)
            .options(selectinload(Category.images))
            .where(Category.id == category_id)
        )

        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        return CategoryReadDTO(
            id=model.id,
            name=model.name,
            description=model.description,
            parent_id=model.parent_id,
            manufacturer_id=model.manufacturer_id,
            images=[
                CategoryImageReadDTO(ordering=image.ordering, image_key=image.object_key)
                for image in sorted(model.images, key=lambda i: i.ordering)
            ],
        )

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[CategoryReadDTO], int]:

        stmt = select(Category).options(selectinload(Category.images))

        count_stmt = select(func.count()).select_from(Category)

        if name:
            stmt = stmt.where(Category.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(Category.name.ilike(f"%{name}%"))

        stmt = stmt.order_by(Category.id).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [
            CategoryReadDTO(
                id=model.id,
                name=model.name,
                description=model.description,
                parent_id=model.parent_id,
                manufacturer_id=model.manufacturer_id,
                images=[
                    CategoryImageReadDTO(ordering=image.ordering, image_key=image.object_key)
                    for image in sorted(model.images, key=lambda i: i.ordering)
                ],
            )
            for model in result.scalars().all()
        ]
        total = count_result.scalar() or 0
        return items, total
