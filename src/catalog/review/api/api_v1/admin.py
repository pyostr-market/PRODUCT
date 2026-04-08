"""API admin endpoints для audit логов отзывов."""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.catalog.review.api.schemas.review import ReviewAuditListResponse, ReviewAuditReadSchema
from src.catalog.review.composition import ReviewComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

review_admin_router = APIRouter(
    tags=["Отзывы (Admin)"],
)


@review_admin_router.get(
    "/audit",
    summary="Аудит отзывов",
    description="""
    Возвращает audit логи для отзывов.

    Права:
    - Требуется permission: `review:audit`
    """,
    response_description="Список audit логов",
    responses={
        200: {
            "description": "Audit логи",
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("review:audit"))],
)
async def get_audit_logs(
    review_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    queries = ReviewComposition.build_admin_queries(db)
    items, total = await queries.filter_logs(
        review_id=review_id,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )

    return api_response(
        ReviewAuditListResponse(
            total=total,
            items=[ReviewAuditReadSchema.model_validate(item) for item in items],
        )
    )
