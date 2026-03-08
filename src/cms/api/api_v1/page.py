from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.page_schemas import PageListResponse, PageReadSchema
from src.cms.application.queries.page_queries import PageQueries
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

page_router = APIRouter(tags=["CMS: Pages"])


# Public endpoints - GET по ID и slug
@page_router.get(
    "/{page_id}",
    summary="Получить страницу по ID",
    response_description="Страница с блоками",
    description="""
    Возвращает детальную информацию о странице по идентификатору.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Отображение страницы по ID.
    - Получение контента для фронтенда.
    """,
)
async def get_page_by_id(
    page_id: int = Path(..., description="ID страницы"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_page_queries(db)
    result = await queries.get_by_id(page_id)

    if not result:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"message": "Страница не найдена", "code": "page_not_found"}}
        )

    return api_response(PageReadSchema.model_validate(result))


@page_router.get(
    "/{slug}",
    summary="Получить страницу по slug",
    response_description="Страница с блоками",
    description="""
    Возвращает детальную информацию о странице по URL идентификатору (slug).

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Отображение страницы по URL.
    - Получение контента для фронтенда.
    """,
)
async def get_page(
    slug: str = Path(..., description="URL идентификатор страницы"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_page_queries(db)
    result = await queries.get_by_slug(slug)

    if not result:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"message": "Страница не найдена", "code": "page_not_found"}}
        )

    return api_response(PageReadSchema.model_validate(result))


@page_router.get(
    "/search",
    summary="Поиск страниц по заголовку",
    response_description="Список страниц",
    description="""
    Поиск страниц по частичному совпадению в заголовке (LIKE).

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам).

    Сценарии:
    - Поиск страниц по названию.
    - Фильтрация в админке.
    """,
)
async def search_pages(
    q: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_page_queries(db)
    items, total = await queries.search(query=q, limit=limit, offset=offset)

    return api_response(
        PageListResponse(
            total=total,
            items=[PageReadSchema.model_validate(i) for i in items],
        )
    )


@page_router.get(
    "",
    summary="Получить список страниц",
    response_description="Список страниц",
    description="""
    Возвращает список страниц с фильтрацией и пагинацией.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам).

    Сценарии:
    - Получение списка страниц для админки.
    - Фильтрация по заголовку и статусу.
    """,
)
async def get_all_pages(
    title: Optional[str] = Query(None, description="Фильтр по заголовку"),
    is_published: Optional[bool] = Query(None, description="Фильтр по статусу публикации"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_page_queries(db)
    items, total = await queries.filter(
        title=title,
        is_published=is_published,
        limit=limit,
        offset=offset,
    )

    return api_response(
        PageListResponse(
            total=total,
            items=[PageReadSchema.model_validate(i) for i in items],
        )
    )
