from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.api.schemas.schemas import (
    ManufacturerListResponse,
    ManufacturerReadSchema,
)
from src.catalog.manufacturer.composition import ManufacturerComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

manufacturer_q_router = APIRouter(
    tags=["Производители"],
)


# GET BY ID
@manufacturer_q_router.get(
    "/{manufacturer_id}",
    summary="Получить производителя по ID",
    description="""
    Возвращает производителя по его идентификатору.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Загрузка данных производителя в карточке.
    - Проверка корректности привязки категорий/товаров к бренду.
    """,
    response_description="Данные производителя в стандартной обёртке API",
    responses={
        200: {
            "description": "Производитель найден",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 3,
                            "name": "Acme Devices",
                            "description": "Мировой производитель электроники",
                        },
                    }
                }
            },
        },
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

# GET BY ID
@manufacturer_q_router.get(
    "",
    summary="Получить список производителей",
    description="""
    Возвращает список производителей с возможностью:

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Построение справочника брендов в UI.
    - Поиск производителя по подстроке имени.

    Поддерживается:
    - фильтрации по имени (частичное совпадение)
    - пагинации (limit, offset)
    """,
    response_description="Список производителей в стандартной обёртке API",
    responses={
        200: {
            "description": "Список успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 2,
                            "items": [
                                {
                                    "id": 3,
                                    "name": "Acme Devices",
                                    "description": "Мировой производитель электроники",
                                },
                                {
                                    "id": 4,
                                    "name": "Nova Tech",
                                    "description": None,
                                },
                            ],
                        },
                    }
                }
            },
        },
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
