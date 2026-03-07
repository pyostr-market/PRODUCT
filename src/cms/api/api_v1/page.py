from typing import Optional

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.page_schemas import PageReadSchema
from src.cms.application.queries.page_queries import PageQueries
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

page_router = APIRouter(tags=["CMS: Pages"])


# Public endpoints - только для получения страниц по slug
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
