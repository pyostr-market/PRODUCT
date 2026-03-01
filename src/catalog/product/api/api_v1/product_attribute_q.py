from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import (
    ProductAttributeListResponse,
    ProductAttributeReadSchema,
)
from src.catalog.product.composition import ProductComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

product_attribute_q_router = APIRouter(
    tags=["Атрибуты продуктов"],
)


@product_attribute_q_router.get(
    "/attribute/{attribute_id}",
    summary="Получить атрибут продукта по ID",
    description="""
    Возвращает атрибут продукта по его идентификатору.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Загрузка данных атрибута для отображения в фильтре каталога.
    - Проверка корректности привязки товаров к атрибуту.
    """,
    response_description="Данные атрибута продукта в стандартной обёртке API",
    responses={
        200: {
            "description": "Атрибут продукта найден",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 10,
                            "name": "RAM",
                            "is_filterable": True,
                        },
                    }
                }
            },
        },
        404: {"description": "Атрибут продукта не найден"},
    },
)
async def get_product_attribute_by_id(
    attribute_id: int,
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_product_attribute_queries(db)
    dto = await queries.get_by_id(attribute_id)

    if not dto:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Атрибут продукта не найден")

    return api_response(
        ProductAttributeReadSchema.model_validate(dto)
    )


@product_attribute_q_router.get(
    "/attribute",
    summary="Получить список атрибутов продуктов",
    description="""
    Возвращает список атрибутов продуктов с возможностью поиска по имени.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Построение справочника атрибутов в UI.
    - Поиск атрибута по подстроке имени.

    Поддерживается:
    - фильтрации по имени (частичное совпадение, поиск по полю name)
    - пагинации (limit, offset)
    """,
    response_description="Список атрибутов продуктов в стандартной обёртке API",
    responses={
        200: {
            "description": "Список атрибутов успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 2,
                            "items": [
                                {
                                    "id": 10,
                                    "name": "RAM",
                                    "is_filterable": True,
                                },
                                {
                                    "id": 11,
                                    "name": "Цвет",
                                    "is_filterable": True,
                                },
                            ],
                        },
                    }
                }
            },
        },
    },
)
async def filter_product_attributes(
    name: str | None = Query(
        None,
        description="Фильтр по имени (частичное совпадение, поиск по полю name)"
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
    queries = ProductComposition.build_product_attribute_queries(db)
    items, total = await queries.filter(name, limit, offset)

    return api_response(
        ProductAttributeListResponse(
            total=total,
            items=[
                ProductAttributeReadSchema.model_validate(i)
                for i in items
            ],
        )
    )
