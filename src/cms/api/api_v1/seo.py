from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.seo_schemas import SeoCreateSchema, SeoMetaResponse, SeoReadSchema, SeoUpdateSchema
from src.cms.application.commands.create_seo import CreateSeoCommand
from src.cms.application.commands.delete_seo import DeleteSeoCommand
from src.cms.application.commands.update_seo import UpdateSeoCommand
from src.cms.application.dto.cms_dto import SeoCreateDTO, SeoUpdateDTO
from src.cms.application.queries.seo_queries import SeoQueries
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

seo_router = APIRouter(tags=["CMS: SEO"])


# Admin endpoints - должны быть зарегистрированы ПЕРЕД public endpoints
@seo_router.post(
    "/admin",
    summary="Создать SEO данные (admin)",
    description="""
    Создаёт SEO данные для страницы.

    Права:
    - Требуется permission: `cms:create`

    Сценарии:
    - Добавление meta тегов для страницы.
    - Настройка SEO оптимизации.
    """,
    response_description="Созданные SEO данные",
    responses={
        200: {"description": "SEO данные успешно созданы"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Страница не найдена"},
    },
    dependencies=[Depends(require_permissions("cms:create"))],
)
async def create_seo(
    schema: SeoCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_create_seo_command(db)
    dto = SeoCreateDTO(
        page_slug=schema.page_slug,
        title=schema.title,
        description=schema.description,
        keywords=schema.keywords,
        og_image_id=schema.og_image_id,
    )
    result = await command.execute(dto)

    return api_response(SeoReadSchema.model_validate(result))


@seo_router.put(
    "/admin/{seo_id}",
    summary="Обновить SEO данные (admin)",
    description="""
    Обновляет SEO данные по идентификатору.

    Права:
    - Требуется permission: `cms:update`

    Сценарии:
    - Изменение meta тегов.
    - Обновление keywords или description.
    """,
    response_description="Обновленные SEO данные",
    responses={
        200: {"description": "SEO данные успешно обновлены"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "SEO данные не найдены"},
    },
    dependencies=[Depends(require_permissions("cms:update"))],
)
async def update_seo(
    seo_id: int,
    schema: SeoUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_update_seo_command(db)
    dto = SeoUpdateDTO(
        title=schema.title,
        description=schema.description,
        keywords=schema.keywords,
        og_image_id=schema.og_image_id,
    )
    result = await command.execute(seo_id, dto)

    return api_response(SeoReadSchema.model_validate(result))


@seo_router.delete(
    "/admin/{seo_id}",
    summary="Удалить SEO данные (admin)",
    description="""
    Удаляет SEO данные по идентификатору.

    Права:
    - Требуется permission: `cms:delete`

    Сценарии:
    - Удаление устаревших SEO данных.
    """,
    response_description="Результат удаления",
    responses={
        200: {"description": "SEO данные успешно удалены"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "SEO данные не найдены"},
    },
    dependencies=[Depends(require_permissions("cms:delete"))],
)
async def delete_seo(
    seo_id: int,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_delete_seo_command(db)
    result = await command.execute(seo_id)

    return api_response({"success": result, "seo_id": seo_id})


@seo_router.get(
    "/admin/{seo_id}",
    summary="Получить SEO данные по ID (admin)",
    description="""
    Возвращает детальную информацию о SEO данных по идентификатору.

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Получение SEO для админки.
    """,
    response_description="SEO данные",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def get_seo_by_id(
    seo_id: int = Path(..., description="ID SEO данных"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_seo_queries(db)
    result = await queries.get_by_id(seo_id)

    if not result:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"message": "SEO данные не найдены", "code": "seo_not_found"}}
        )

    return api_response(SeoReadSchema.model_validate(result))


@seo_router.get(
    "/admin/search",
    summary="Поиск SEO данных (admin)",
    description="""
    Поиск SEO данных по частичному совпадению в title или description (LIKE).

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Поиск SEO в админке.
    """,
    response_description="Список SEO данных",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def search_seo(
    q: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_seo_queries(db)
    items, total = await queries.search(query=q, limit=limit, offset=offset)

    return api_response(
        SeoListResponse(
            total=total,
            items=[SeoReadSchema.model_validate(i) for i in items],
        )
    )


@seo_router.get(
    "/admin",
    summary="Получить все SEO данные (admin)",
    description="""
    Возвращает список всех SEO данных с фильтрацией и пагинацией.

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Управление SEO в админке.
    """,
    response_description="Список SEO данных",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def get_all_seo(
    page_slug: Optional[str] = Query(None, description="Фильтр по slug страницы"),
    title: Optional[str] = Query(None, description="Фильтр по заголовку"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_seo_queries(db)
    items, total = await queries.filter(
        page_slug=page_slug,
        title=title,
        limit=limit,
        offset=offset,
    )

    return api_response(
        SeoListResponse(
            total=total,
            items=[SeoReadSchema.model_validate(i) for i in items],
        )
    )


# Public endpoints
@seo_router.get(
    "/{page_slug}/meta",
    summary="Получить meta теги для страницы",
    description="""
    Возвращает meta теги для указанной страницы.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам).

    Сценарии:
    - Получение SEO данных для фронтенда.
    - Динамическая генерация meta тегов.
    """,
    response_description="Meta теги",
    responses={
        200: {"description": "Meta теги успешно получены"},
        404: {"description": "SEO данные не найдены"},
    },
)
async def get_seo_meta(
    page_slug: str = Path(..., description="Slug страницы"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_seo_queries(db)
    result = await queries.get_by_page_slug(page_slug)

    if not result:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"message": "SEO данные не найдены", "code": "seo_not_found"}}
        )

    # Формируем meta ответ
    meta = SeoMetaResponse(
        title=result.title,
        description=result.description,
        keywords=', '.join(result.keywords) if result.keywords else None,
        og_image_id=result.og_image_id,
    )

    return api_response(meta)
