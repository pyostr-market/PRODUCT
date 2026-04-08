from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.regions.api.schemas.schemas import (
    RegionListResponse,
    RegionReadSchema,
)
from src.regions.composition import RegionComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

region_q_router = APIRouter(
    tags=["Регионы"],
)


@region_q_router.get(
    "/{region_id}",
    summary="Получить регион по ID",
    description="""
    Возвращает карточку региона по идентификатору.

    Права:
    - Требуется permission: `region:view`

    Сценарии:
    - Загрузка данных региона для привязки товара.
    - Просмотр карточки региона в админ-панели.
    """,
    response_description="Регион в стандартной обёртке API",
    responses={
        200: {
            "description": "Регион найден",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "name": "Северо-Западный",
                            "parent_id": None,
                        },
                    }
                }
            },
        },
        404: {"description": "Регион не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("region:view"))],
)
async def get_by_id(
    region_id: int,
    db: AsyncSession = Depends(get_db),
):
    queries = RegionComposition.build_queries(db)
    dto = await queries.get_by_id(region_id)
    return api_response(RegionReadSchema.model_validate(dto))


@region_q_router.get(
    "",
    summary="Получить список регионов",
    description="""
    Возвращает список регионов с фильтрами и пагинацией.

    Права:
    - Требуется permission: `region:view`

    Сценарии:
    - Выбор региона при создании товара.
    - Поиск регионов в справочнике.
    - Получение дочерних регионов для построения иерархии.
    """,
    response_description="Список регионов в стандартной обёртке API",
    responses={
        200: {
            "description": "Список регионов успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 2,
                            "items": [
                                {
                                    "id": 1,
                                    "name": "Северо-Западный",
                                    "parent_id": None,
                                },
                                {
                                    "id": 2,
                                    "name": "Санкт-Петербург",
                                    "parent_id": 1,
                                },
                            ],
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("region:view"))],
)
async def filter_regions(
    name: str | None = Query(None, description="Фильтр по имени"),
    parent_id: int | None = Query(None, description="Фильтр по родительскому региону"),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = RegionComposition.build_queries(db)
    items, total = await queries.filter(name, parent_id, limit, offset)

    return api_response(
        RegionListResponse(
            total=total,
            items=[RegionReadSchema.model_validate(i) for i in items],
        )
    )


@region_q_router.get(
    "/{parent_id}/children",
    summary="Получить дочерние регионы",
    description="""
    Возвращает список дочерних регионов для указанного родительского региона.

    Права:
    - Требуется permission: `region:view`

    Сценарии:
    - Построение дерева регионов.
    - Получение списка городов внутри области.
    """,
    response_description="Список дочерних регионов",
    responses={
        200: {
            "description": "Дочерние регионы успешно получены",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "id": 2,
                                "name": "Санкт-Петербург",
                                "parent_id": 1,
                            },
                        ],
                    }
                }
            },
        },
        404: {"description": "Родительский регион не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("region:view"))],
)
async def get_children(
    parent_id: int,
    db: AsyncSession = Depends(get_db),
):
    queries = RegionComposition.build_queries(db)
    items = await queries.get_children(parent_id)

    return api_response([RegionReadSchema.model_validate(i) for i in items])
