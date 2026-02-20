from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.suppliers.api.schemas.schemas import (
    SupplierListResponse,
    SupplierReadSchema,
)
from src.catalog.suppliers.composition import SupplierComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

supplier_q_router = APIRouter(tags=["Поставщики"])


@supplier_q_router.get(
    "/{supplier_id}",
    summary="Получить поставщика по ID",
    description="""
    Возвращает карточку поставщика по идентификатору.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Загрузка данных поставщика перед оформлением закупки.
    - Просмотр карточки контрагента в админ-панели.
    """,
    response_description="Поставщик в стандартной обёртке API",
    responses={
        200: {
            "description": "Поставщик найден",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 210,
                            "name": "ООО Поставка Плюс",
                            "contact_email": "sales@supply-plus.example",
                            "phone": "+7-999-123-45-67",
                        },
                    }
                }
            },
        },
        404: {"description": "Поставщик не найден"},
    },
)
async def get_by_id(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
):
    queries = SupplierComposition.build_queries(db)
    dto = await queries.get_by_id(supplier_id)
    return api_response(SupplierReadSchema.model_validate(dto))


@supplier_q_router.get(
    "/",
    summary="Получить список поставщиков",
    description="""
    Возвращает список поставщиков с фильтром по имени и пагинацией.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Выбор поставщика при создании товара.
    - Поиск контрагентов в справочнике.
    """,
    response_description="Список поставщиков в стандартной обёртке API",
    responses={
        200: {
            "description": "Список поставщиков успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 2,
                            "items": [
                                {
                                    "id": 210,
                                    "name": "ООО Поставка Плюс",
                                    "contact_email": "sales@supply-plus.example",
                                    "phone": "+7-999-123-45-67",
                                },
                                {
                                    "id": 211,
                                    "name": "ИП Логистика",
                                    "contact_email": None,
                                    "phone": "+7-999-111-22-33",
                                },
                            ],
                        },
                    }
                }
            },
        }
    },
)
async def filter_suppliers(
    name: str | None = Query(None, description="Фильтр по имени"),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = SupplierComposition.build_queries(db)
    items, total = await queries.filter(name, limit, offset)

    return api_response(
        SupplierListResponse(
            total=total,
            items=[SupplierReadSchema.model_validate(i) for i in items],
        )
    )
