from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.page_schemas import (
    PageAuditListResponse,
    PageAuditReadSchema,
)
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

admin_page_router = APIRouter(
    tags=["CMS: Pages"],
)


@admin_page_router.get(
    "/audit",
    summary="Получить аудит-логи страниц",
    description="""
    Возвращает журнал изменений по страницам с фильтрами и пагинацией.

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Разбор инцидентов и восстановление хронологии изменений.
    - Контроль действий пользователей в административном интерфейсе.
    - Отслеживание истории изменений контента страниц.
    """,
    response_description="Список записей аудита страниц",
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
                                    "page_id": 1,
                                    "action": "update",
                                    "old_data": {"title": "О компании"},
                                    "new_data": {"title": "О компании (обновлено)"},
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
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def get_audit_logs(
    page_id: Optional[int] = Query(None, description="Фильтр по ID страницы"),
    user_id: Optional[int] = Query(None, description="Фильтр по ID пользователя"),
    action: Optional[str] = Query(None, description="Фильтр по действию (create, update, delete)"),
    limit: int = Query(20, le=100, description="Максимальное количество записей"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: AsyncSession = Depends(get_db),
):
    # Заглушка: аудит логи для CMS пока не реализованы
    # В будущем здесь будет вызов queries.filter_logs()
    return api_response(
        PageAuditListResponse(
            total=0,
            items=[],
        )
    )
