from fastapi import APIRouter, Depends
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
from src.core.db.database import get_db

feature_flag_router = APIRouter(tags=["CMS: Feature Flags"])


# Admin endpoints - должны быть зарегистрированы ПЕРЕД public endpoints
@feature_flag_router.post(
    "/admin",
    summary="Создать feature flag (admin)",
    response_description="Созданный флаг",
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
    response_description="Обновленный флаг",
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
    response_description="Результат удаления",
)
async def delete_flag(
    flag_id: int,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_delete_feature_flag_command(db)
    result = await command.execute(flag_id)

    return api_response({"success": result, "flag_id": flag_id})


# Public endpoints
@feature_flag_router.get(
    "",
    summary="Получить все feature flags",
    response_description="Список флагов",
)
async def get_all_flags(
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_feature_flag_queries(db)
    items = await queries.get_all()

    return api_response(
        FeatureFlagListResponse(
            total=len(items),
            items=[FeatureFlagReadSchema.model_validate(i) for i in items],
        )
    )


@feature_flag_router.get(
    "/enabled",
    summary="Получить включенные feature flags",
    response_description="Список включенных флагов",
)
async def get_enabled_flags(
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_feature_flag_queries(db)
    enabled = await queries.get_enabled()

    return api_response(FeatureFlagEnabledListResponse(enabled_flags=enabled))
