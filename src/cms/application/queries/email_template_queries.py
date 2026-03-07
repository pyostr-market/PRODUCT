from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.application.dto.cms_dto import EmailTemplateReadDTO
from src.cms.infrastructure.models.email_template import CmsEmailTemplate


class EmailTemplateQueries:
    """Query класс для получения email шаблонов."""

    def __init__(self, db: AsyncSession):
        self.db = db

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
