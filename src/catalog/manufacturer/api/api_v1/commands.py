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
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

manufacturer_commands_router = APIRouter(
    tags=["Производители"],
)


# CREATE
@manufacturer_commands_router.post(
    "",
    status_code=200,
    summary="Создать производителя",
    description="""
    Создаёт нового производителя.

    Права:
    - Требуется permission: `manufacturer:create`

    Сценарии:
    - Добавление нового бренда в справочник.
    - Подготовка данных для привязки категорий к производителю.
    """,
    response_description="Созданный производитель в стандартной обёртке API",
    responses={
        200: {
            "description": "Производитель успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 3,
                            "name": "Acme Devices",
                            "description": "Мировой производитель электроники",
                        },
                    }
                }
            },
        },
        400: {"description": "Некорректные данные (имя слишком короткое)"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Производитель уже существует"},
    },
    dependencies=[Depends(require_permissions("manufacturer:create"))],
)
async def create(
    payload: ManufacturerCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
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

    Права:
    - Требуется permission: `manufacturer:update`

    Сценарии:
    - Переименование бренда.
    - Обновление описания производителя.
    """,
    response_description="Обновлённый производитель в стандартной обёртке API",
    responses={
        200: {
            "description": "Производитель успешно обновлён",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 3,
                            "name": "Acme Devices International",
                            "description": "Обновлённое описание бренда",
                        },
                    }
                }
            },
        },
        400: {"description": "Имя слишком короткое"},
        404: {"description": "Производитель не найден"},
        403: {"description": "Недостаточно прав"},
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

    Права:
    - Требуется permission: `manufacturer:delete`

    Сценарии:
    - Удаление неактуального производителя.
    - Очистка ошибочно созданной записи.
    """,
    responses={
        200: {
            "description": "Производитель успешно удалён",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        404: {"description": "Производитель не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("manufacturer:delete"))],
)
async def delete(
    manufacturer_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ManufacturerComposition.build_delete_command(db)
    await commands.execute(
        manufacturer_id,
        user=user,
    )

    return api_response({"deleted": True})
