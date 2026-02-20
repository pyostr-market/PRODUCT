from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.audit import CategoryAuditListResponse, CategoryAuditReadSchema
from src.catalog.category.composition import CategoryComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

admin_category_router = APIRouter(tags=["Categories Admin"])


@admin_category_router.get(
    "/audit",
    summary="Получить аудит-логи категорий",
    dependencies=[Depends(require_permissions("category:audit"))],
)
async def get_audit_logs(
    category_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = CategoryComposition.build_admin_queries(db)

    items, total = await queries.filter_logs(
        category_id=category_id,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )

    return api_response(
        CategoryAuditListResponse(
            total=total,
            items=[CategoryAuditReadSchema.model_validate(i) for i in items],
        )
    )
