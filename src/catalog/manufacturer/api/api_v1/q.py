from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.api.schemas.schemas import (
    ManufacturerListResponse,
    ManufacturerReadSchema,
)
from src.catalog.manufacturer.composition import ManufacturerComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.db.database import get_db

manufacturer_q_router = APIRouter(
    tags=["Manufacturers"]
)


# GET BY ID
@manufacturer_q_router.get(
    "/{manufacturer_id}",
    summary="Получить производителя по ID",
    description="""
    Возвращает производителя по его идентификатору.
    """,
    response_description="Данные производителя",
    responses={
        200: {"description": "Производитель найден"},
        404: {"description": "Производитель не найден"},
    },
)
async def get_by_id(
    manufacturer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    ### Возможные статусы:

    - **200** — найден
    - **404** — не найден
    """

    queries = ManufacturerComposition.build_queries(db)
    dto = await queries.get_by_id(manufacturer_id)

    return api_response(
        ManufacturerReadSchema.model_validate(dto)
    )

# FILTER + PAGINATION
@manufacturer_q_router.get(
    "/",
    summary="Получить список производителей",
    description="""
    Возвращает список производителей с возможностью:
    
    - фильтрации по имени (частичное совпадение)
    - пагинации (limit, offset)
    """,
    response_description="Список производителей",
    responses={
        200: {"description": "Список успешно получен"},
    },
)
async def filter_manufacturers(
    name: str | None = Query(
        None,
        description="Фильтр по имени (частичное совпадение)"
    ),
    limit: int = Query(
        10,
        le=100,
        description="Количество записей (макс. 100)"
    ),
    offset: int = Query(
        0,
        description="Смещение"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    ### Возможные статусы:

    - **200** — список успешно получен
    """
    queries = ManufacturerComposition.build_queries(db)
    items, total = await queries.filter(name, limit, offset)

    return api_response(
        ManufacturerListResponse(
            total=total,
            items=[
                ManufacturerReadSchema.model_validate(i)
                for i in items
            ],
        )
    )