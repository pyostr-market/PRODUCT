from fastapi import APIRouter, Depends, Path
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
