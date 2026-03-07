from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.domain.aggregates.email_template import EmailTemplateAggregate
from src.cms.domain.repository.email_template import EmailTemplateRepository
from src.cms.infrastructure.models.email_template import CmsEmailTemplate


class SqlAlchemyEmailTemplateRepository(EmailTemplateRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, template_id: int) -> Optional[EmailTemplateAggregate]:
        model = await self.db.get(CmsEmailTemplate, template_id)
        if not model:
            return None

        return self._to_aggregate(model)

    async def get_by_key(self, key: str) -> Optional[EmailTemplateAggregate]:
        stmt = select(CmsEmailTemplate).where(CmsEmailTemplate.key == key)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def get_all(self, is_active: Optional[bool] = True) -> list[EmailTemplateAggregate]:
        stmt = select(CmsEmailTemplate)

        if is_active is not None:
            stmt = stmt.where(CmsEmailTemplate.is_active == is_active)

        stmt = stmt.order_by(CmsEmailTemplate.key)
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_aggregate(model) for model in models]

    async def create(self, aggregate: EmailTemplateAggregate) -> EmailTemplateAggregate:
        model = CmsEmailTemplate(
            key=aggregate.key,
            subject=aggregate.subject,
            body_html=aggregate.body_html,
            body_text=aggregate.body_text,
            variables=aggregate.variables,
            is_active=aggregate.is_active,
        )

        self.db.add(model)
        await self.db.flush()

        aggregate.template_id = model.id
        return aggregate

    async def delete(self, template_id: int) -> bool:
        model = await self.db.get(CmsEmailTemplate, template_id)
        if not model:
            return False

        await self.db.delete(model)
        return True

    async def update(self, aggregate: EmailTemplateAggregate) -> EmailTemplateAggregate:
        model = await self.db.get(CmsEmailTemplate, aggregate.id)
        if not model:
            raise ValueError(f"Email template with id {aggregate.id} not found")

        model.subject = aggregate.subject
        model.body_html = aggregate.body_html
        model.body_text = aggregate.body_text
        model.variables = aggregate.variables
        model.is_active = aggregate.is_active

        await self.db.flush()
        return aggregate

    def _to_aggregate(self, model: CmsEmailTemplate) -> EmailTemplateAggregate:
        return EmailTemplateAggregate(
            template_id=model.id,
            key=model.key,
            subject=model.subject,
            body_html=model.body_html,
            body_text=model.body_text,
            variables=model.variables or [],
            is_active=model.is_active,
        )
