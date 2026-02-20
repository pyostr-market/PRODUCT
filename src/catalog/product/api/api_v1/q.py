from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import ProductListResponse, ProductReadSchema
from src.catalog.product.composition import ProductComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

product_q_router = APIRouter(tags=["Товары"])


@product_q_router.get(
    "/related/variants",
    summary="Получить связанные товары",
    description="""
    Возвращает список похожих или связанных товаров по `product_id` и/или `name`.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Блок «Похожие товары» в карточке.
    - Поиск альтернатив по названию.
    """,
    response_description="Список связанных товаров в стандартной обёртке API",
    responses={
        200: {
            "description": "Список связанных товаров успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 1,
                            "items": [
                                {
                                    "id": 3002,
                                    "name": "Смартфон X Lite",
                                    "description": "Более доступная версия",
                                    "price": "39990.00",
                                    "category_id": 101,
                                    "supplier_id": 210,
                                    "product_type_id": 5,
                                    "images": [],
                                    "attributes": [
                                        {"name": "RAM", "value": "6 GB", "is_filterable": True}
                                    ],
                                }
                            ],
                        },
                    }
                }
            },
        }
    },
)
async def related_products(
    product_id: int | None = Query(None),
    name: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_queries(db)
    items = await queries.related(product_id=product_id, name=name)

    return api_response(
        ProductListResponse(
            total=len(items),
            items=[ProductReadSchema.model_validate(item) for item in items],
        )
    )


@product_q_router.get(
    "/{product_id}",
    summary="Получить товар по ID",
    description="""
    Возвращает карточку товара по идентификатору.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Открытие страницы товара.
    - Получение товара перед редактированием.
    """,
    response_description="Товар в стандартной обёртке API",
    responses={
        200: {
            "description": "Товар найден",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 3001,
                            "name": "Смартфон X",
                            "description": "Флагманская модель",
                            "price": "59990.00",
                            "category_id": 101,
                            "supplier_id": 210,
                            "product_type_id": 5,
                            "images": [
                                {
                                    "image_url": "https://cdn.example.com/product/smartphone-x-main.jpg",
                                    "is_main": True,
                                }
                            ],
                            "attributes": [
                                {"name": "RAM", "value": "8 GB", "is_filterable": True}
                            ],
                        },
                    }
                }
            },
        },
        404: {"description": "Товар не найден"},
    },
)
async def get_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    queries = ProductComposition.build_queries(db)
    dto = await queries.get_by_id(product_id)
    return api_response(ProductReadSchema.model_validate(dto))


@product_q_router.get(
    "/",
    summary="Получить список товаров",
    description="""
    Возвращает список товаров с фильтрацией и пагинацией.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Каталог товаров на витрине.
    - Выборка товаров по категории или типу.
    """,
    response_description="Список товаров в стандартной обёртке API",
    responses={
        200: {
            "description": "Список товаров успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 2,
                            "items": [
                                {
                                    "id": 3001,
                                    "name": "Смартфон X",
                                    "description": "Флагманская модель",
                                    "price": "59990.00",
                                    "category_id": 101,
                                    "supplier_id": 210,
                                    "product_type_id": 5,
                                    "images": [],
                                    "attributes": [],
                                },
                                {
                                    "id": 3002,
                                    "name": "Смартфон X Lite",
                                    "description": "Более доступная версия",
                                    "price": "39990.00",
                                    "category_id": 101,
                                    "supplier_id": 210,
                                    "product_type_id": 5,
                                    "images": [],
                                    "attributes": [],
                                },
                            ],
                        },
                    }
                }
            },
        }
    },
)
async def filter_products(
    name: str | None = Query(None),
    category_id: int | None = Query(None),
    product_type_id: int | None = Query(None),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_queries(db)
    items, total = await queries.filter(
        name=name,
        category_id=category_id,
        product_type_id=product_type_id,
        limit=limit,
        offset=offset,
    )

    return api_response(
        ProductListResponse(
            total=total,
            items=[ProductReadSchema.model_validate(item) for item in items],
        )
    )
