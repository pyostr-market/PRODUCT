from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.domain.aggregates.faq import FaqAggregate
from src.cms.domain.repository.faq import FaqRepository
from src.cms.infrastructure.models.faq import CmsFaq


class SqlAlchemyFaqRepository(FaqRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, faq_id: int) -> Optional[FaqAggregate]:
        model = await self.db.get(CmsFaq, faq_id)
        if not model:
            return None

        return self._to_aggregate(model)

    async def get_all(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = True,
    ) -> list[FaqAggregate]:
        stmt = select(CmsFaq)

        if category is not None:
            stmt = stmt.where(CmsFaq.category == category)

        if is_active is not None:
            stmt = stmt.where(CmsFaq.is_active == is_active)

        stmt = stmt.order_by(CmsFaq.order, CmsFaq.id)
        result = await self.db.execute(stmt)
        models = result.scalars().all()

        return [self._to_aggregate(model) for model in models]

    async def create(self, aggregate: FaqAggregate) -> FaqAggregate:
        model = CmsFaq(
            question=aggregate.question,
            answer=aggregate.answer,
            category=aggregate.category,
            order=aggregate.order,
            is_active=aggregate.is_active,
        )

        self.db.add(model)
        await self.db.flush()

        aggregate._set_id(model.id)
        return aggregate

    async def delete(self, faq_id: int) -> bool:
        model = await self.db.get(CmsFaq, faq_id)
        if not model:
            return False

        await self.db.delete(model)
        return True

    async def update(self, aggregate: FaqAggregate) -> FaqAggregate:
        model = await self.db.get(CmsFaq, aggregate.id)
        if not model:
            raise ValueError(f"FAQ with id {aggregate.id} not found")

        model.question = aggregate.question
        model.answer = aggregate.answer
        model.category = aggregate.category
        model.order = aggregate.order
        model.is_active = aggregate.is_active

        await self.db.flush()
        return aggregate

    def _to_aggregate(self, model: CmsFaq) -> FaqAggregate:
        return FaqAggregate(
            faq_id=model.id,
            question=model.question,
            answer=model.answer,
            category=model.category,
            order=model.order,
            is_active=model.is_active,
        )
