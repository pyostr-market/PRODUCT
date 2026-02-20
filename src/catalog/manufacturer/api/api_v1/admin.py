from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.api.schemas.audit import (
    ManufacturerAuditListResponse,
    ManufacturerAuditReadSchema,
)
from src.catalog.manufacturer.composition import ManufacturerComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

admin_manufacturer_router = APIRouter(
    tags=["Производители"]
)


@admin_manufacturer_router.get(
    "/audit",
    summary="Получить аудит-логи производителей",
    description="""
    Возвращает журнал аудита изменений производителей.

    Права:
    - Требуется permission: `manufacturer:audit`

    Сценарии:
    - Контроль изменений справочника брендов.
    - Анализ действий пользователя по конкретному производителю.
    """,
    response_description="Список записей аудита производителей",
    responses={
        200: {
            "description": "Логи аудита успешно получены",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 1,
                            "items": [
                                {
                                    "id": 810,
                                    "manufacturer_id": 3,
                                    "action": "update",
                                    "old_data": {"name": "Acme Devices"},
                                    "new_data": {"name": "Acme Devices International"},
                                    "user_id": 42,
                                    "created_at": "2026-02-20T10:30:00Z",
                                }
                            ],
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("manufacturer:audit"))],
)
async def get_audit_logs(
    manufacturer_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """
    Доступно только администраторам.
    """

    queries = ManufacturerComposition.build_admin_queries(db)

    items, total = await queries.filter_logs(
        manufacturer_id=manufacturer_id,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )

    return api_response(
        ManufacturerAuditListResponse(
            total=total,
            items=[
                ManufacturerAuditReadSchema.model_validate(i)
                for i in items
            ]
        )
    )
