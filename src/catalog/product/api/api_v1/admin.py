from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.audit import ProductAuditListResponse, ProductAuditReadSchema
from src.catalog.product.composition import ProductComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

admin_product_router = APIRouter(tags=["Products Admin"])


@admin_product_router.get(
    "/audit",
    summary="Получить аудит-логи товаров",
    dependencies=[Depends(require_permissions("product:audit"))],
)
async def get_audit_logs(
    product_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_admin_queries(db)
    items, total = await queries.filter_logs(
        product_id=product_id,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )

    return api_response(
        ProductAuditListResponse(
            total=total,
            items=[ProductAuditReadSchema.model_validate(i) for i in items],
        )
    )
