from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.application.dto.cms_dto import EmailTemplateReadDTO
from src.cms.infrastructure.models.email_template import CmsEmailTemplate


class EmailTemplateQueries:
    """Query класс для получения email шаблонов."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, template_id: int) -> Optional[EmailTemplateReadDTO]:
        """Получить шаблон по ID."""
        stmt = select(CmsEmailTemplate).where(CmsEmailTemplate.id == template_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def get_by_key(self, key: str) -> Optional[EmailTemplateReadDTO]:
        """Получить шаблон по ключу."""
        stmt = select(CmsEmailTemplate).where(
            CmsEmailTemplate.key == key,
            CmsEmailTemplate.is_active == True,
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def filter(
        self,
        is_active: Optional[bool] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list[EmailTemplateReadDTO], int]:
        """
        Фильтрация email шаблонов с пагинацией.

        Args:
            is_active: Фильтр по статусу активности
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Кортеж из списка DTO и общего количества записей
        """
        stmt = select(CmsEmailTemplate)

        if is_active is not None:
            stmt = stmt.where(CmsEmailTemplate.is_active == is_active)

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsEmailTemplate.key).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

    async def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> Tuple[list[EmailTemplateReadDTO], int]:
        """
        Поиск email шаблонов по key и subject (LIKE).

        Args:
            query: Поисковый запрос
            limit: Максимальное количество записей
            offset: Смещение для пагинации

        Returns:
            Кортеж из списка DTO и общего количества записей
        """
        stmt = select(CmsEmailTemplate)

        if query:
            stmt = stmt.where(
                (CmsEmailTemplate.key.ilike(f"%{query}%")) |
                (CmsEmailTemplate.subject.ilike(f"%{query}%"))
            )

        # Получаем общее количество
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(CmsEmailTemplate.key).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models], total

    async def get_all(self, is_active: bool = True) -> list[EmailTemplateReadDTO]:
        """Получить все шаблоны."""
        stmt = select(CmsEmailTemplate)

        if is_active is not None:
            stmt = stmt.where(CmsEmailTemplate.is_active == is_active)

        stmt = stmt.order_by(CmsEmailTemplate.key)
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_read_dto(model) for model in models]

    def _to_read_dto(self, model: CmsEmailTemplate) -> EmailTemplateReadDTO:
        return EmailTemplateReadDTO(
            id=model.id,
            key=model.key,
            subject=model.subject,
            body_html=model.body_html,
            body_text=model.body_text,
            variables=model.variables or [],
            is_active=model.is_active,
        )
