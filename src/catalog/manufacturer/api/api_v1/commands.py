from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.api.schemas.schemas import (
    ManufacturerCreateSchema,
    ManufacturerReadSchema,
    ManufacturerUpdateSchema,
)
from src.catalog.manufacturer.application.dto.manufacturer import (
    ManufacturerCreateDTO,
    ManufacturerUpdateDTO,
)
from src.catalog.manufacturer.composition import ManufacturerComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions, get_current_user
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

manufacturer_commands_router = APIRouter(
    tags=["Manufacturers"]
)


# CREATE
@manufacturer_commands_router.post(
    "/",
    status_code=200,
    summary="Создать производителя",
    description="""
    Создаёт нового производителя.
    
    - Имя должно быть уникальным
    - Минимальная длина имени — 2 символа
    """,
    response_description="Созданный производитель",
    responses={
        200: {"description": "Производитель успешно создан"},
        400: {"description": "Некорректные данные (имя слишком короткое)"},
        409: {"description": "Производитель уже существует"},
    },
    dependencies=[Depends(require_permissions("manufacturer:create"))],
)
async def create(
    payload: ManufacturerCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    ### Возможные статусы:

    - **201** — успешно создан
    - **400** — имя слишком короткое
    - **409** — производитель уже существует
    """

    commands = ManufacturerComposition.build_create_command(db)

    dto = await commands.execute(
        ManufacturerCreateDTO(**payload.model_dump()),
        user=user,
    )

    return api_response(
        ManufacturerReadSchema.model_validate(dto)
    )

# UPDATE
@manufacturer_commands_router.put(
    "/{manufacturer_id}",
    summary="Обновить производителя",
    description="""
    Обновляет существующего производителя.
    
    Можно изменить:
    - имя
    - описание
    """,
    response_description="Обновлённый производитель",
    responses={
        200: {"description": "Производитель успешно обновлён"},
        400: {"description": "Имя слишком короткое"},
        404: {"description": "Производитель не найден"},
        409: {"description": "Конфликт уникальности имени"},
    },
    dependencies=[Depends(require_permissions("manufacturer:update"))],
)
async def update(
    manufacturer_id: int,
    payload: ManufacturerUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    ### Возможные статусы:

    - **200** — успешно обновлён
    - **400** — некорректные данные
    - **404** — производитель не найден
    - **409** — конфликт уникальности
    """

    commands = ManufacturerComposition.build_update_command(db)

    dto = await commands.execute(
        manufacturer_id,
        ManufacturerUpdateDTO(**payload.model_dump()),
        user=user,
    )

    return api_response(
        ManufacturerReadSchema.model_validate(dto)
    )
# DELETE
@manufacturer_commands_router.delete(
    "/{manufacturer_id}",
    summary="Удалить производителя",
    description="""
    Удаляет производителя по ID.
    
    Удаление каскадное:
    - связанные категории также будут удалены
    """,
    responses={
        200: {"description": "Производитель успешно удалён"},
        404: {"description": "Производитель не найден"},
    },
    dependencies=[Depends(require_permissions("manufacturer:delete"))],
)
async def delete(
    manufacturer_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    ### Возможные статусы:

    - **200** — успешно удалён
    - **404** — производитель не найден
    """

    commands = ManufacturerComposition.build_delete_command(db)
    await commands.execute(
        manufacturer_id,
        user=user,
    )

    return api_response({"deleted": True})