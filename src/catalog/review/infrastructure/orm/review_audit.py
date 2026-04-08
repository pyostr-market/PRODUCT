"""SQLAlchemy реализация репозитория для audit логов отзывов."""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.review.application.dto.review import ReviewAuditDTO
from src.catalog.review.domain.repository.review_audit import (
    ReviewAuditQueryRepository,
    ReviewAuditRepository,
)
from src.catalog.review.infrastructure.models.review_audit_log import ReviewAuditLog


class SqlAlchemyReviewAuditRepository(ReviewAuditRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, dto: ReviewAuditDTO) -> None:
        model = ReviewAuditLog(
            review_id=dto.review_id,
            action=dto.action,
            old_data=dto.old_data,
            new_data=dto.new_data,
            user_id=dto.user_id,
            fio=dto.fio,
        )
        self.db.add(model)
        await self.db.flush()


class SqlAlchemyReviewAuditQueryRepository(ReviewAuditQueryRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def filter_logs(
        self,
        review_id: Optional[int] = None,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[Any], int]:
        filters = []
        if review_id is not None:
            filters.append(ReviewAuditLog.review_id == review_id)
        if user_id is not None:
            filters.append(ReviewAuditLog.user_id == user_id)
        if action is not None:
            filters.append(ReviewAuditLog.action == action)

        # Счётчик
        count_stmt = (
            select(func.count(ReviewAuditLog.id))
            .where(*filters)
        )
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Данные
        stmt = (
            select(ReviewAuditLog)
            .where(*filters)
            .order_by(ReviewAuditLog.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        items = result.scalars().all()

        return items, total
