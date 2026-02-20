from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.suppliers.api.schemas.audit import (
    SupplierAuditListResponse,
    SupplierAuditReadSchema,
)
from src.catalog.suppliers.composition import SupplierComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

admin_supplier_router = APIRouter(tags=["Suppliers Admin"])


@admin_supplier_router.get(
    "/audit",
    summary="Получить аудит-логи поставщиков",
    dependencies=[Depends(require_permissions("supplier:audit"))],
)
async def get_audit_logs(
    supplier_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = SupplierComposition.build_admin_queries(db)

    items, total = await queries.filter_logs(
        supplier_id=supplier_id,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )

    return api_response(
        SupplierAuditListResponse(
            total=total,
            items=[SupplierAuditReadSchema.model_validate(i) for i in items],
        )
    )
