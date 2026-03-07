from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.application.dto.cms_dto import FaqReadDTO
from src.cms.infrastructure.models.faq import CmsFaq


class FaqQueries:
    """Query класс для получения FAQ."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        category: Optional[str] = None,
        is_active: bool = True,
    ) -> list[FaqReadDTO]:
        """Получить все FAQ с фильтрацией."""
        stmt = select(CmsFaq)

        if category is not None:
            stmt = stmt.where(CmsFaq.category == category)

        if is_active is not None:
            stmt = stmt.where(CmsFaq.is_active == is_active)

        stmt = stmt.order_by(CmsFaq.category, CmsFaq.order, CmsFaq.id)
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models]

    async def get_categories(self) -> list[str]:
        """Получить все категории FAQ."""
        stmt = select(CmsFaq.category).where(
            CmsFaq.category.isnot(None),
            CmsFaq.is_active == True,
        ).distinct()
        result = await self.db.execute(stmt)
        return [row[0] for row in result.all() if row[0]]

    def _to_read_dto(self, model: CmsFaq) -> FaqReadDTO:
        return FaqReadDTO(
            id=model.id,
            question=model.question,
            answer=model.answer,
            category=model.category,
            order=model.order,
            is_active=model.is_active,
        )
