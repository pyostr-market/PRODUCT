from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.audit import (
    CategoryAuditListResponse,
    CategoryAuditReadSchema,
)
from src.catalog.category.composition import CategoryComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

admin_category_router = APIRouter(
    tags=["Категории"],
)


@admin_category_router.get(
    "/audit",
    summary="Получить аудит-логи категорий",
    description="""
    Возвращает журнал изменений по категориям с фильтрами и пагинацией.

    Права:
    - Требуется permission: `category:audit`

    Сценарии:
    - Разбор инцидентов и восстановление хронологии изменений.
    - Контроль действий пользователей в административном интерфейсе.
    """,
    response_description="Список записей аудита категорий",
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
                                    "id": 501,
                                    "category_id": 101,
                                    "action": "update",
                                    "old_data": {"name": "Смартфоны"},
                                    "new_data": {"name": "Смартфоны и гаджеты"},
                                    "user_id": 42,
                                    "created_at": "2026-02-20T10:15:00Z",
                                }
                            ],
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
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
