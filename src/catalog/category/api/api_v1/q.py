from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.schemas import (
    CategoryListResponse,
    CategoryReadSchema,
)
from src.catalog.category.composition import CategoryComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

category_q_router = APIRouter(
    tags=["Категории"],
)


@category_q_router.get(
    "/{category_id}",
    summary="Получить категорию по ID",
    description="""
    Возвращает детальную информацию о категории.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Открытие карточки категории.
    - Получение данных перед редактированием.
    """,
    response_description="Категория в стандартной обёртке API",
    responses={
        200: {
            "description": "Категория найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 101,
                            "name": "Смартфоны",
                            "description": "Смартфоны и аксессуары",
                            "parent_id": None,
                            "manufacturer_id": 3,
                            "images": [
                                {
                                    "ordering": 0,
                                    "image_url": "https://cdn.example.com/category/smartphones-main.jpg",
                                }
                            ],
                        },
                    }
                }
            },
        },
        404: {"description": "Категория не найдена"},
    },
)
async def get_by_id(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    queries = CategoryComposition.build_queries(db)
    dto = await queries.get_by_id(category_id)
    return api_response(CategoryReadSchema.model_validate(dto))


@category_q_router.get(
    "",
    summary="Получить список категорий",
    description="""
    Возвращает список категорий с пагинацией и фильтрацией по имени.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Построение каталога категорий в интерфейсе.
    - Поиск категорий по части названия.
    """,
    response_description="Список категорий в стандартной обёртке API",
    responses={
        200: {
            "description": "Список категорий успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 2,
                            "items": [
                                {
                                    "id": 101,
                                    "name": "Смартфоны",
                                    "description": "Смартфоны и аксессуары",
                                    "parent_id": None,
                                    "manufacturer_id": 3,
                                    "images": [
                                        {
                                            "ordering": 0,
                                            "image_url": "https://cdn.example.com/category/smartphones-main.jpg",
                                        }
                                    ],
                                },
                                {
                                    "id": 102,
                                    "name": "Планшеты",
                                    "description": "Планшеты всех брендов",
                                    "parent_id": None,
                                    "manufacturer_id": 3,
                                    "images": [],
                                },
                            ],
                        },
                    }
                }
            },
        }
    },
)
async def filter_categories(
    name: str | None = Query(None, description="Фильтр по имени"),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    queries = CategoryComposition.build_queries(db)
    items, total = await queries.filter(name, limit, offset)

    return api_response(
        CategoryListResponse(
            total=total,
            items=[CategoryReadSchema.model_validate(i) for i in items],
        )
    )
