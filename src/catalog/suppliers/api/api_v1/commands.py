from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.suppliers.api.schemas.schemas import (
    SupplierCreateSchema,
    SupplierReadSchema,
    SupplierUpdateSchema,
)
from src.catalog.suppliers.application.dto.supplier import (
    SupplierCreateDTO,
    SupplierUpdateDTO,
)
from src.catalog.suppliers.composition import SupplierComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

supplier_commands_router = APIRouter(tags=["Поставщики"])


@supplier_commands_router.post(
    "/",
    status_code=200,
    summary="Создать поставщика",
    description="""
    Создаёт нового поставщика.

    Права:
    - Требуется permission: `supplier:create`

    Сценарии:
    - Добавление нового контрагента для закупок.
    - Первичное заполнение справочника поставщиков.
    """,
    response_description="Созданный поставщик в стандартной обёртке API",
    responses={
        200: {
            "description": "Поставщик успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 210,
                            "name": "ООО Поставка Плюс",
                            "contact_email": "sales@supply-plus.example",
                            "phone": "+7-999-123-45-67",
                        },
                    }
                }
            },
        },
        400: {"description": "Некорректные данные"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Поставщик с таким именем уже существует"},
    },
    dependencies=[Depends(require_permissions("supplier:create"))],
)
async def create(
    payload: SupplierCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = SupplierComposition.build_create_command(db)
    dto = await commands.execute(SupplierCreateDTO(**payload.model_dump()), user=user)
    return api_response(SupplierReadSchema.model_validate(dto))


@supplier_commands_router.put(
    "/{supplier_id}",
    summary="Обновить поставщика",
    description="""
    Обновляет поставщика по идентификатору.

    Права:
    - Требуется permission: `supplier:update`

    Сценарии:
    - Обновление контактного e-mail и телефона.
    - Переименование поставщика после изменения юр.лица.
    """,
    response_description="Обновлённый поставщик в стандартной обёртке API",
    responses={
        200: {
            "description": "Поставщик успешно обновлён",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 210,
                            "name": "ООО Поставка Плюс",
                            "contact_email": "support@supply-plus.example",
                            "phone": "+7-999-123-45-68",
                        },
                    }
                }
            },
        },
        400: {"description": "Некорректные данные"},
        404: {"description": "Поставщик не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("supplier:update"))],
)
async def update(
    supplier_id: int,
    payload: SupplierUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = SupplierComposition.build_update_command(db)
    dto = await commands.execute(supplier_id, SupplierUpdateDTO(**payload.model_dump()), user=user)
    return api_response(SupplierReadSchema.model_validate(dto))


@supplier_commands_router.delete(
    "/{supplier_id}",
    summary="Удалить поставщика",
    description="""
    Удаляет поставщика по идентификатору.

    Права:
    - Требуется permission: `supplier:delete`

    Сценарии:
    - Очистка справочника от неактуальных поставщиков.
    - Удаление дублей после миграции данных.
    """,
    response_description="Флаг успешного удаления",
    responses={
        200: {
            "description": "Поставщик успешно удалён",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        404: {"description": "Поставщик не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("supplier:delete"))],
)
async def delete(
    supplier_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = SupplierComposition.build_delete_command(db)
    await commands.execute(supplier_id, user=user)
    return api_response({"deleted": True})
