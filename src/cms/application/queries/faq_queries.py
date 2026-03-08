from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.application.dto.cms_dto import FaqReadDTO
from src.cms.infrastructure.models.faq import CmsFaq


class FaqQueries:
    """Query класс для получения FAQ."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, faq_id: int) -> Optional[FaqReadDTO]:
        """Получить FAQ по ID."""
        stmt = select(CmsFaq).where(CmsFaq.id == faq_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def get_all(
        self,
        category: Optional[str] = None,
        is_active: bool = True,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list[FaqReadDTO], int]:
        """Получить все FAQ с фильтрацией и пагинацией."""
        stmt = select(CmsFaq)

        if category is not None:
            stmt = stmt.where(CmsFaq.category == category)

        if is_active is not None:
            stmt = stmt.where(CmsFaq.is_active == is_active)

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsFaq.category, CmsFaq.order, CmsFaq.id).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list[FaqReadDTO], int]:
        """
        Поиск FAQ по вопросу и ответу (LIKE).

        Args:
            query: Поисковый запрос
            category: Фильтр по категории
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Кортеж из списка DTO и общего количества записей
        """
        stmt = select(CmsFaq)

        if query:
            stmt = stmt.where(
                (CmsFaq.question.ilike(f"%{query}%")) | (CmsFaq.answer.ilike(f"%{query}%"))
            )

        if category is not None:
            stmt = stmt.where(CmsFaq.category == category)

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsFaq.category, CmsFaq.order, CmsFaq.id).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

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
