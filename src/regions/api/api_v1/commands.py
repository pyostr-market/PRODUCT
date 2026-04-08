from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.regions.api.schemas.schemas import (
    RegionCreateSchema,
    RegionReadSchema,
    RegionUpdateSchema,
)
from src.regions.application.dto.region import (
    RegionCreateDTO,
    RegionUpdateDTO,
)
from src.regions.composition import RegionComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

region_commands_router = APIRouter(
    tags=["Регионы"],
)


@region_commands_router.post(
    "",
    status_code=200,
    summary="Создать регион",
    description="""
    Создаёт новый регион.

    Права:
    - Требуется permission: `region:create`

    Сценарии:
    - Добавление нового региона (например, Северо-Западный).
    - Создание дочернего региона (например, Санкт-Петербург внутри Северо-Западного).
    """,
    response_description="Созданный регион в стандартной обёртке API",
    responses={
        200: {
            "description": "Регион успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "name": "Северо-Западный",
                            "parent_id": None,
                        },
                    }
                }
            },
        },
        400: {"description": "Некорректные данные"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Регион с таким именем уже существует"},
    },
    dependencies=[Depends(require_permissions("region:create"))],
)
async def create(
    payload: RegionCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = RegionComposition.build_create_command(db)
    dto = await commands.execute(RegionCreateDTO(**payload.model_dump()), user=user)
    return api_response(RegionReadSchema.model_validate(dto))


@region_commands_router.put(
    "/{region_id}",
    summary="Обновить регион",
    description="""
    Обновляет регион по идентификатору.

    Права:
    - Требуется permission: `region:update`

    Сценарии:
    - Переименование региона.
    - Изменение родительского региона (перенос в другую иерархию).
    """,
    response_description="Обновлённый регион в стандартной обёртке API",
    responses={
        200: {
            "description": "Регион успешно обновлён",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "name": "Северо-Западный федеральный округ",
                            "parent_id": None,
                        },
                    }
                }
            },
        },
        400: {"description": "Некорректные данные"},
        404: {"description": "Регион не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("region:update"))],
)
async def update(
    region_id: int,
    payload: RegionUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = RegionComposition.build_update_command(db)
    dto = await commands.execute(region_id, RegionUpdateDTO(**payload.model_dump()), user=user)
    return api_response(RegionReadSchema.model_validate(dto))


@region_commands_router.delete(
    "/{region_id}",
    summary="Удалить регион",
    description="""
    Удаляет регион по идентификатору.

    Права:
    - Требуется permission: `region:delete`

    Сценарии:
    - Очистка справочника от неактуальных регионов.
    - Удаление дублей после миграции данных.
    """,
    response_description="Флаг успешного удаления",
    responses={
        200: {
            "description": "Регион успешно удалён",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        404: {"description": "Регион не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("region:delete"))],
)
async def delete(
    region_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = RegionComposition.build_delete_command(db)
    await commands.execute(region_id, user=user)
    return api_response({"deleted": True})
