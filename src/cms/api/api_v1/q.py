from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.page_schemas import (
    PageListResponse,
    PageReadSchema,
)
from src.cms.application.queries.page_queries import PageQueries
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

page_q_router = APIRouter(
    tags=["CMS: Pages"],
)


@page_q_router.get(
    "",
    summary="Получить список страниц",
    description="""
    Возвращает список опубликованных страниц с пагинацией.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Построение списка страниц для навигации.
    - Получение всех доступных статических страниц.
    - Отображение списка страниц в административном интерфейсе.
    """,
    response_description="Список страниц в стандартной обёртке API",
    responses={
        200: {
            "description": "Список страниц успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 3,
                            "items": [
                                {
                                    "id": 1,
                                    "slug": "about-us",
                                    "title": "О компании",
                                    "is_published": True,
                                    "blocks": [
                                        {
                                            "id": 1,
                                            "page_id": 1,
                                            "block_type": "text",
                                            "order": 0,
                                            "data": {"content": "Добро пожаловать"},
                                            "is_active": True,
                                        }
                                    ],
                                },
                                {
                                    "id": 2,
                                    "slug": "delivery",
                                    "title": "Доставка и оплата",
                                    "is_published": True,
                                    "blocks": [],
                                },
                                {
                                    "id": 3,
                                    "slug": "contacts",
                                    "title": "Контакты",
                                    "is_published": True,
                                    "blocks": [],
                                },
                            ],
                        },
                    }
                }
            },
        }
    },
)
async def filter_pages(
    title: Optional[str] = Query(None, description="Фильтр по заголовку"),
    is_published: Optional[bool] = Query(None, description="Фильтр по статусу публикации"),
    limit: int = Query(10, le=100, description="Максимальное количество записей"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_page_queries(db)
    items, total = await queries.filter(title=title, is_published=is_published, limit=limit, offset=offset)

    return api_response(
        PageListResponse(
            total=total,
            items=[PageReadSchema.model_validate(i) for i in items],
        )
    )


@page_q_router.get(
    "/{page_id}",
    summary="Получить страницу по ID",
    description="""
    Возвращает детальную информацию о странице по идентификатору.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Открытие карточки страницы.
    - Получение данных перед редактированием.
    - Проверка существования страницы.
    """,
    response_description="Страница в стандартной обёртке API",
    responses={
        200: {
            "description": "Страница найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "slug": "about-us",
                            "title": "О компании",
                            "is_published": True,
                            "blocks": [
                                {
                                    "id": 1,
                                    "page_id": 1,
                                    "block_type": "text",
                                    "order": 0,
                                    "data": {"content": "Добро пожаловать"},
                                    "is_active": True,
                                },
                                {
                                    "id": 2,
                                    "page_id": 1,
                                    "block_type": "image",
                                    "order": 1,
                                    "data": {"upload_id": 1, "alt": "Баннер"},
                                    "is_active": True,
                                },
                            ],
                        },
                    }
                }
            },
        },
        404: {
            "description": "Страница не найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "page_not_found",
                            "message": "Страница не найдена",
                            "details": {"page_id": 9999},
                        },
                    }
                }
            },
        },
    },
)
async def get_by_id(
    page_id: int,
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_page_queries(db)
    dto = await queries.get_by_id(page_id)
    return api_response(PageReadSchema.model_validate(dto))


@page_q_router.get(
    "/slug/{slug}",
    summary="Получить страницу по slug",
    description="""
    Возвращает детальную информацию о странице по URL идентификатору (slug).

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Отображение страницы по URL.
    - Получение контента для фронтенда.
    - Проверка существования страницы по slug.
    """,
    response_description="Страница в стандартной обёртке API",
    responses={
        200: {
            "description": "Страница найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "slug": "about-us",
                            "title": "О компании",
                            "is_published": True,
                            "blocks": [
                                {
                                    "id": 1,
                                    "page_id": 1,
                                    "block_type": "text",
                                    "order": 0,
                                    "data": {"content": "Добро пожаловать"},
                                    "is_active": True,
                                },
                            ],
                        },
                    }
                }
            },
        },
        404: {
            "description": "Страница не найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "page_not_found",
                            "message": "Страница не найдена",
                            "details": {"slug": "non-existent"},
                        },
                    }
                }
            },
        },
    },
)
async def get_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_page_queries(db)
    dto = await queries.get_by_slug(slug)
    return api_response(PageReadSchema.model_validate(dto))
