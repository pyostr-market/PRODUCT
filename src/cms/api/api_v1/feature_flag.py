from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.feature_flag_schemas import (
    FeatureFlagCreateSchema,
    FeatureFlagEnabledListResponse,
    FeatureFlagListResponse,
    FeatureFlagReadSchema,
    FeatureFlagUpdateSchema,
)
from src.cms.application.commands.create_feature_flag import CreateFeatureFlagCommand
from src.cms.application.commands.delete_feature_flag import DeleteFeatureFlagCommand
from src.cms.application.commands.update_feature_flag import UpdateFeatureFlagCommand
from src.cms.application.dto.cms_dto import FeatureFlagCreateDTO, FeatureFlagUpdateDTO
from src.cms.application.queries.feature_flag_queries import FeatureFlagQueries
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

feature_flag_router = APIRouter(tags=["CMS: Feature Flags"])


# Admin endpoints - должны быть зарегистрированы ПЕРЕД public endpoints
@feature_flag_router.post(
    "/admin",
    summary="Создать feature flag (admin)",
    description="""
    Создаёт новый feature flag.

    Права:
    - Требуется permission: `cms:create`

    Сценарии:
    - Включение/выключение функциональности.
    - A/B тестирование функций.
    """,
    response_description="Созданный флаг",
    responses={
        200: {"description": "Feature flag успешно создан"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Feature flag с таким key уже существует"},
    },
    dependencies=[Depends(require_permissions("cms:create"))],
)
async def create_flag(
    schema: FeatureFlagCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_create_feature_flag_command(db)
    dto = FeatureFlagCreateDTO(
        key=schema.key,
        enabled=schema.enabled,
        description=schema.description,
    )
    result = await command.execute(dto)

    return api_response(FeatureFlagReadSchema.model_validate(result))


@feature_flag_router.put(
    "/admin/{flag_id}",
    summary="Обновить feature flag (admin)",
    description="""
    Обновляет feature flag по идентификатору.

    Права:
    - Требуется permission: `cms:update`

    Сценарии:
    - Включение/выключение флага.
    - Изменение описания флага.
    """,
    response_description="Обновленный флаг",
    responses={
        200: {"description": "Feature flag успешно обновлен"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Feature flag не найден"},
    },
    dependencies=[Depends(require_permissions("cms:update"))],
)
async def update_flag(
    flag_id: int,
    schema: FeatureFlagUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_update_feature_flag_command(db)
    dto = FeatureFlagUpdateDTO(
        enabled=schema.enabled,
        description=schema.description,
    )
    result = await command.execute(flag_id, dto)

    return api_response(FeatureFlagReadSchema.model_validate(result))


@feature_flag_router.delete(
    "/admin/{flag_id}",
    summary="Удалить feature flag (admin)",
    description="""
    Удаляет feature flag по идентификатору.

    Права:
    - Требуется permission: `cms:delete`

    Сценарии:
    - Удаление устаревшего флага.
    """,
    response_description="Результат удаления",
    responses={
        200: {"description": "Feature flag успешно удален"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Feature flag не найден"},
    },
    dependencies=[Depends(require_permissions("cms:delete"))],
)
async def delete_flag(
    flag_id: int,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_delete_feature_flag_command(db)
    result = await command.execute(flag_id)

    return api_response({"success": result, "flag_id": flag_id})


@feature_flag_router.get(
    "/admin/{flag_id}",
    summary="Получить feature flag по ID (admin)",
    description="""
    Возвращает детальную информацию о feature flag по идентификатору.

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Получение флага для админки.
    """,
    response_description="Feature flag",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def get_flag_by_id(
    flag_id: int = Path(..., description="ID флага"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_feature_flag_queries(db)
    result = await queries.get_by_id(flag_id)

    if not result:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"message": "Feature flag не найден", "code": "feature_flag_not_found"}}
        )

    return api_response(FeatureFlagReadSchema.model_validate(result))


@feature_flag_router.get(
    "/admin/search",
    summary="Поиск feature flags (admin)",
    description="""
    Поиск feature flags по частичному совпадению в key или description (LIKE).

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Поиск флагов в админке.
    """,
    response_description="Список флагов",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def search_flags(
    q: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_feature_flag_queries(db)
    items, total = await queries.search(query=q, limit=limit, offset=offset)

    return api_response(
        FeatureFlagListResponse(
            total=total,
            items=[FeatureFlagReadSchema.model_validate(i) for i in items],
        )
    )


@feature_flag_router.get(
    "/admin",
    summary="Получить все feature flags (admin)",
    description="""
    Возвращает список всех feature flags с пагинацией.

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Получение списка всех флагов для админки.
    """,
    response_description="Список флагов",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def get_all_flags_admin(
    enabled: Optional[bool] = Query(None, description="Фильтр по статусу"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_feature_flag_queries(db)
    items, total = await queries.filter(enabled=enabled, limit=limit, offset=offset)

    return api_response(
        FeatureFlagListResponse(
            total=total,
            items=[FeatureFlagReadSchema.model_validate(i) for i in items],
        )
    )


# Public endpoints
@feature_flag_router.get(
    "",
    summary="Получить все feature flags",
    description="""
    Возвращает список всех feature flags.

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Получение списка всех флагов для админки.
    """,
    response_description="Список флагов",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def get_all_flags(
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_feature_flag_queries(db)
    items, total = await queries.filter(limit=limit, offset=offset)

    return api_response(
        FeatureFlagListResponse(
            total=total,
            items=[FeatureFlagReadSchema.model_validate(i) for i in items],
        )
    )


@feature_flag_router.get(
    "/enabled",
    summary="Получить включенные feature flags",
    description="""
    Возвращает список включенных feature flags.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам).

    Сценарии:
    - Проверка активных функций на фронтенде.
    - Динамическое включение функциональности.
    """,
    response_description="Список включенных флагов",
)
async def get_enabled_flags(
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_feature_flag_queries(db)
    enabled = await queries.get_enabled()

    return api_response(FeatureFlagEnabledListResponse(enabled_flags=enabled))
