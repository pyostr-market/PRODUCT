from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.regions.api.schemas.audit import (
    RegionAuditListResponse,
    RegionAuditReadSchema,
)
from src.regions.composition import RegionComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

admin_region_router = APIRouter(
    tags=["Регионы"],
)


@admin_region_router.get(
    "/audit",
    summary="Получить аудит-логи регионов",
    description="""
    Возвращает аудит-логи по изменениям регионов.

    Права:
    - Требуется permission: `region:audit`

    Сценарии:
    - Проверка, кто изменил название региона.
    - Анализ действий пользователей при конфликте данных.
    """,
    response_description="Список записей аудита регионов",
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
                                    "id": 1,
                                    "region_id": 1,
                                    "action": "update",
                                    "old_data": {"name": "Северо-Западный"},
                                    "new_data": {"name": "Северо-Западный федеральный округ"},
                                    "user_id": 42,
                                    "created_at": "2026-04-08T10:20:00Z",
                                }
                            ],
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("region:audit"))],
)
async def get_audit_logs(
    region_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = RegionComposition.build_admin_queries(db)

    items, total = await queries.filter_logs(
        region_id=region_id,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )

    return api_response(
        RegionAuditListResponse(
            total=total,
            items=[RegionAuditReadSchema.model_validate(i) for i in items],
        )
    )
