from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.audit import (
    ProductAuditListResponse,
    ProductAuditReadSchema,
)
from src.catalog.product.api.schemas.product_type import (
    ProductTypeAuditListResponse,
    ProductTypeAuditReadSchema,
)
from src.catalog.product.composition import ProductComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

admin_product_router = APIRouter(
    tags=["Товары"],
)


@admin_product_router.get(
    "/audit",
    summary="Получить аудит-логи товаров",
    description="""
    Возвращает журнал аудита действий над товарами.

    Права:
    - Требуется permission: `product:audit`

    Сценарии:
    - Анализ изменений цены и атрибутов.
    - Поиск пользователя, выполнившего удаление или обновление товара.
    """,
    response_description="Список записей аудита товаров",
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
                                    "id": 701,
                                    "product_id": 3001,
                                    "action": "update",
                                    "old_data": {"price": "59990.00"},
                                    "new_data": {"price": "64990.00"},
                                    "user_id": 42,
                                    "created_at": "2026-02-20T10:25:00Z",
                                }
                            ],
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
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


# ==================== ProductType Admin ====================

admin_product_type_router = APIRouter(
    tags=["Типы продуктов"],
)


@admin_product_type_router.get(
    "/type/audit",
    summary="Получить аудит-логи типов продуктов",
    description="""
    Возвращает журнал аудита действий над типами продуктов.

    Права:
    - Требуется permission: `product_type:audit`

    Сценарии:
    - Анализ изменений типов продуктов.
    - Поиск пользователя, выполнившего удаление или обновление типа.
    """,
    response_description="Список записей аудита типов продуктов",
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
                                    "id": 801,
                                    "product_type_id": 5,
                                    "action": "update",
                                    "old_data": {"name": "Смартфоны"},
                                    "new_data": {"name": "Смартфоны Pro"},
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
    dependencies=[Depends(require_permissions("product_type:audit"))],
)
async def get_product_type_audit_logs(
    product_type_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_product_type_admin_queries(db)
    items, total = await queries.filter_logs(
        product_type_id=product_type_id,
        user_id=user_id,
        action=action,
        limit=limit,
        offset=offset,
    )

    return api_response(
        ProductTypeAuditListResponse(
            total=total,
            items=[ProductTypeAuditReadSchema.model_validate(i) for i in items],
        )
    )
