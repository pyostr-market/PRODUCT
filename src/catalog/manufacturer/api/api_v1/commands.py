from typing import Optional

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

    **Формат `image`** (объект с upload_id):
    ```json
    {"upload_id": 4275}
    ```

    Где:
    - `upload_id`: ID предварительно загруженного изображения через UploadHistory
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
                            "image": {
                                "upload_id": 1,
                                "image_url": "https://cdn.example.com/manufacturers/acme-main.jpg"
                            },
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

    image_dto = None
    if payload.image:
        from src.catalog.manufacturer.application.dto.manufacturer import ManufacturerImageInputDTO
        image_dto = ManufacturerImageInputDTO(upload_id=payload.image.upload_id)

    dto = await commands.execute(
        ManufacturerCreateDTO(
            name=payload.name,
            description=payload.description,
            image=image_dto,
        ),
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

    Работа с изображением:
    - Изображение передаётся через `image` (JSON-объект операции).
    - Операция имеет поле `action`: `create`, `update`, `delete`, `pass`.
    - `create` — добавить/заменить изображение (требуется `upload_id`).
    - `update` — обновить изображение (требуется `upload_id`).
    - `delete` — удалить изображение.
    - `pass` — сохранить существующее изображение.

    Пример `image`:
    ```json
    {"action": "create", "upload_id": 4275}
    ```
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
                            "image": {
                                "upload_id": 1,
                                "image_url": "https://cdn.example.com/manufacturers/acme-main.jpg"
                            },
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
    image_dto = None
    if payload.image:
        from src.catalog.manufacturer.application.dto.manufacturer import ManufacturerImageOperationDTO
        image_dto = ManufacturerImageOperationDTO(
            action=payload.image.action,
            upload_id=payload.image.upload_id,
            image_url=payload.image.image_url,
        )

    commands = ManufacturerComposition.build_update_command(db)

    dto = await commands.execute(
        manufacturer_id,
        ManufacturerUpdateDTO(
            name=payload.name,
            description=payload.description,
            image=image_dto,
        ),
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
