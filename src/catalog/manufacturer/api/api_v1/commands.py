import json
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.api.schemas.schemas import (
    ManufacturerReadSchema,
)
from src.catalog.manufacturer.application.dto.manufacturer import (
    ManufacturerCreateDTO,
    ManufacturerImageInputDTO,
    ManufacturerImageOperationDTO,
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


async def _parse_image_json(
    image_json: str | None,
) -> Optional[ManufacturerImageInputDTO]:
    """
    Парсинг JSON объекта изображения для создания производителя.

    Формат image_json:
    ```json
    {"upload_id": 1}
    ```
    """
    if not image_json:
        return None

    try:
        payload = json.loads(image_json)
    except json.JSONDecodeError as exc:
        from src.catalog.manufacturer.domain.exceptions import (
            ManufacturerInvalidPayload,
        )
        raise ManufacturerInvalidPayload(details={"reason": "invalid_image_json", "error": str(exc)})

    if not isinstance(payload, dict):
        from src.catalog.manufacturer.domain.exceptions import (
            ManufacturerInvalidPayload,
        )
        raise ManufacturerInvalidPayload(details={"reason": "image_must_be_object"})

    upload_id = payload.get("upload_id")
    if not upload_id:
        from src.catalog.manufacturer.domain.exceptions import (
            ManufacturerInvalidPayload,
        )
        raise ManufacturerInvalidPayload(details={"reason": "missing_upload_id"})

    try:
        upload_id = int(upload_id)
    except (ValueError, TypeError):
        from src.catalog.manufacturer.domain.exceptions import (
            ManufacturerInvalidPayload,
        )
        raise ManufacturerInvalidPayload(details={"reason": "upload_id_must_be_int"})

    return ManufacturerImageInputDTO(upload_id=upload_id)


async def _build_image_operation_dto(
    image_json: str | None,
) -> Optional[ManufacturerImageOperationDTO]:
    """
    Построение DTO для операции с изображением при обновлении производителя.

    image_json - JSON-объект операции {action, upload_id}
    """
    if not image_json:
        return None

    try:
        payload = json.loads(image_json)
    except json.JSONDecodeError as exc:
        from src.catalog.manufacturer.domain.exceptions import (
            ManufacturerInvalidPayload,
        )
        raise ManufacturerInvalidPayload(details={"reason": "invalid_image_json", "error": str(exc)})

    if not isinstance(payload, dict):
        from src.catalog.manufacturer.domain.exceptions import (
            ManufacturerInvalidPayload,
        )
        raise ManufacturerInvalidPayload(details={"reason": "image_must_be_object"})

    action = payload.get("action")
    if action not in ("create", "delete", "pass", "update"):
        from src.catalog.manufacturer.domain.exceptions import (
            ManufacturerInvalidPayload,
        )
        raise ManufacturerInvalidPayload(details={"reason": "invalid_action", "action": action})

    return ManufacturerImageOperationDTO(
        action=action,  # type: ignore[arg-type]
        upload_id=payload.get("upload_id"),
        image_url=payload.get("image_url"),
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

    **Формат `image_json`** (объект с upload_id):
    ```json
    {"action": "create", "upload_id": 4275}
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
    name: Annotated[str, Form(...)],
    description: Annotated[Optional[str], Form()] = None,
    image_json: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    image_dto = await _parse_image_json(image_json) if image_json else None

    commands = ManufacturerComposition.build_create_command(db)

    dto = await commands.execute(
        ManufacturerCreateDTO(
            name=name,
            description=description,
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
    - Изображение передаётся через `image_json` (JSON-объект операции).
    - Операция имеет поле `action`: `create`, `update`, `delete`, `pass`.
    - `create` — добавить/заменить изображение (требуется `upload_id`).
    - `update` — обновить изображение (требуется `upload_id`).
    - `delete` — удалить изображение.
    - `pass` — сохранить существующее изображение.

    Пример `image_json`:
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
    name: Annotated[Optional[str], Form()] = None,
    description: Annotated[Optional[str], Form()] = None,
    image_json: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    image_dto = await _build_image_operation_dto(image_json) if image_json else None

    commands = ManufacturerComposition.build_update_command(db)

    dto = await commands.execute(
        manufacturer_id,
        ManufacturerUpdateDTO(
            name=name,
            description=description,
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
