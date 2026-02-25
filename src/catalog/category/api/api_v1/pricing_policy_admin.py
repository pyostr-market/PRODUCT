from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.pricing_policy_audit import (
    CategoryPricingPolicyAuditListResponse,
    CategoryPricingPolicyAuditReadSchema,
)
from src.catalog.category.composition import CategoryPricingPolicyComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

admin_pricing_policy_router = APIRouter(
    tags=["Тарификация категории"],
)


@admin_pricing_policy_router.get(
    "/audit",
    summary="Получить аудит-логи политики ценообразования категории",
    description="""
    Возвращает журнал изменений по политикам ценообразования с фильтрами и пагинацией.

    Права:
    - Требуется permission: `category_pricing_policy:audit`

    Сценарии:
    - Разбор инцидентов и восстановление хронологии изменений.
    - Контроль действий пользователей в административном интерфейсе.
    - Аудит изменений наценок, комиссий и налогов.
    """,
    response_description="Список записей аудита политики ценообразования",
    responses={
        200: {
            "description": "Логи аудита успешно получены",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 3,
                            "items": [
                                {
                                    "id": 501,
                                    "pricing_policy_id": 1,
                                    "action": "update",
                                    "old_data": {
                                        "markup_percent": "15.00",
                                        "commission_percent": "5.00",
                                    },
                                    "new_data": {
                                        "markup_percent": "18.00",
                                        "commission_percent": "5.00",
                                    },
                                    "user_id": 42,
                                    "fio": "Иванов Иван",
                                    "created_at": "2026-02-20T10:15:00Z",
                                },
                                {
                                    "id": 500,
                                    "pricing_policy_id": 1,
                                    "action": "create",
                                    "old_data": None,
                                    "new_data": {
                                        "category_id": 101,
                                        "markup_fixed": "100.00",
                                        "markup_percent": "15.00",
                                        "commission_percent": "5.00",
                                        "discount_percent": "2.00",
                                        "tax_rate": "20.00",
                                    },
                                    "user_id": 42,
                                    "fio": "Иванов Иван",
                                    "created_at": "2026-02-19T08:00:00Z",
                                },
                            ],
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("category_pricing_policy:audit"))],
)
async def get_audit_logs(
    pricing_policy_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = CategoryPricingPolicyComposition.build_admin_queries(db)

    items, total = await queries.filter_logs(
        pricing_policy_id=pricing_policy_id,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )

    return api_response(
        CategoryPricingPolicyAuditListResponse(
            total=total,
            items=[CategoryPricingPolicyAuditReadSchema.model_validate(i) for i in items],
        )
    )
