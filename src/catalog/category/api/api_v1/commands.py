import json
from typing import Annotated, List

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.schemas import CategoryReadSchema
from src.catalog.category.application.dto.category import (
    CategoryCreateDTO,
    CategoryImageInputDTO,
    CategoryImageOperationDTO,
    CategoryUpdateDTO,
)
from src.catalog.category.composition import CategoryComposition
from src.core.api.normalizers import normalize_optional_fk
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

category_commands_router = APIRouter(
    tags=["Категории"],
)


def _parse_images_json(images_json: str | None) -> list[CategoryImageInputDTO]:
    """
    Парсинг JSON массива изображений для создания категории.

    Формат images_json:
    ```json
    [
      {"upload_id": 1, "ordering": 0},
      {"upload_id": 2, "ordering": 1}
    ]
    ```
    """
    if not images_json:
        return []

    try:
        payload = json.loads(images_json)
    except json.JSONDecodeError as exc:
        from src.catalog.category.domain.exceptions import CategoryInvalidImage
        raise CategoryInvalidImage(details={"reason": "invalid_images_json", "error": str(exc)})

    if not isinstance(payload, list):
        from src.catalog.category.domain.exceptions import CategoryInvalidImage
        raise CategoryInvalidImage(details={"reason": "images_must_be_list"})

    mapped = []
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            from src.catalog.category.domain.exceptions import CategoryInvalidImage
            raise CategoryInvalidImage(details={"reason": "image_item_must_be_object"})

        upload_id = item.get("upload_id")
        if not upload_id:
            from src.catalog.category.domain.exceptions import CategoryInvalidImage
            raise CategoryInvalidImage(details={"reason": "missing_upload_id", "index": idx})

        try:
            upload_id = int(upload_id)
        except (ValueError, TypeError):
            from src.catalog.category.domain.exceptions import CategoryInvalidImage
            raise CategoryInvalidImage(details={"reason": "upload_id_must_be_int", "index": idx})

        ordering = item.get("ordering", idx)
        if isinstance(ordering, str):
            try:
                ordering = int(ordering)
            except ValueError:
                ordering = idx

        mapped.append(
            CategoryImageInputDTO(
                upload_id=upload_id,
                ordering=ordering,
            )
        )

    return mapped


async def _build_image_operations_dto(
    images_json: str | None,
) -> list[CategoryImageOperationDTO] | None:
    """
    Построение DTO для операций с изображениями при обновлении категории.

    images_json - JSON-список операций {action, upload_id, ordering}
    """
    if not images_json:
        return None

    try:
        payload = json.loads(images_json)
    except json.JSONDecodeError as exc:
        from src.catalog.category.domain.exceptions import CategoryInvalidImage
        raise CategoryInvalidImage(details={"reason": "invalid_images_json", "error": str(exc)})

    if not isinstance(payload, list):
        from src.catalog.category.domain.exceptions import CategoryInvalidImage
        raise CategoryInvalidImage(details={"reason": "images_must_be_list"})

    operations: list[CategoryImageOperationDTO] = []

    for item in payload:
        if not isinstance(item, dict):
            from src.catalog.category.domain.exceptions import CategoryInvalidImage
            raise CategoryInvalidImage(details={"reason": "image_operation_must_be_object"})

        action = item.get("action")
        if action not in ("create", "delete", "pass", "update"):
            from src.catalog.category.domain.exceptions import CategoryInvalidImage
            raise CategoryInvalidImage(details={"reason": "invalid_action", "action": action})

        op = CategoryImageOperationDTO(
            action=action,
            upload_id=item.get("upload_id"),
            image_url=item.get("image_url"),
            ordering=item.get("ordering"),
        )

        operations.append(op)

    return operations if operations else None


@category_commands_router.post(
    "",
    status_code=200,
    summary="Создать категорию",
    description="""
    Создаёт новую категорию с изображениями.

    Права:
    - Требуется permission: `category:create`

    Сценарии:
    - Инициализация новой ветки каталога.
    - Создание категории с привязкой к производителю.
    - Загрузка набора изображений с явным порядком отображения.

    **Формат `images_json`** (массив объектов с upload_id):
    ```json
    [
      {"upload_id": 1, "ordering": 0},
      {"upload_id": 2, "ordering": 1}
    ]
    ```

    Каждый элемент массива содержит:
    - `upload_id`: ID предварительно загруженного изображения через UploadHistory
    - `ordering`: порядок сортировки (int)
    """,
    response_description="Созданная категория в стандартной обёртке API",
    responses={
        200: {
            "description": "Категория успешно создана",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 101,
                            "name": "Смартфоны",
                            "description": "Смартфоны и аксессуары",
                            "parent_id": None,
                            "manufacturer_id": 3,
                            "images": [
                                {
                                    "upload_id": 10,
                                    "ordering": 0,
                                    "image_url": "https://cdn.example.com/category/smartphones-main.jpg",
                                }
                            ],
                            "parent": None,
                            "manufacturer": {
                                "id": 3,
                                "name": "Acme Devices",
                                "description": "Мировой производитель электроники"
                            },
                        },
                    }
                }
            },
        },
        400: {
            "description": "Некорректный JSON изображений или некорректные входные данные",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_invalid_image",
                            "message": "Некорректный файл изображения категории",
                            "details": {
                                "reason": "invalid_images_json",
                            },
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("category:create"))],
)
async def create(
    name: Annotated[str, Form(...)],
    images_json: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    parent_id: Annotated[int | None, Form()] = None,
    manufacturer_id: Annotated[int | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    images_dto = _parse_images_json(images_json) if images_json else []
    commands = CategoryComposition.build_create_command(db)
    dto = await commands.execute(
        CategoryCreateDTO(
            name=name,
            description=description,
            parent_id=normalize_optional_fk(parent_id),
            manufacturer_id=normalize_optional_fk(manufacturer_id),
            images=images_dto,
        ),
        user=user,
    )
    return api_response(CategoryReadSchema.model_validate(dto))


@category_commands_router.put(
    "/{category_id}",
    summary="Обновить категорию",
    description="""
    Частично обновляет категорию по идентификатору.

    Права:
    - Требуется permission: `category:update`

    Сценарии:
    - Переименование или смена описания категории.
    - Перепривязка к родительской категории или производителю.
    - Полная замена набора изображений категории.

    Работа с изображениями:
    - Изображения передаются через `images_json` (JSON-массив операций).
    - Каждая операция имеет поле `action`: `create`, `update`, `delete`, `pass`.
    - `create` — добавить изображение (требуется `upload_id`).
    - `update` — обновить изображение (требуется `upload_id`).
    - `delete` — удалить изображение (требуется `upload_id`).
    - `pass` — сохранить существующее изображение (требуется `upload_id`).

    Пример `images_json`:
    ```json
    [
      {"action": "pass", "upload_id": 123, "ordering": 0},
      {"action": "update", "upload_id": 124, "ordering": 1},
      {"action": "delete", "upload_id": 456},
      {"action": "create", "upload_id": 789, "ordering": 2}
    ]
    ```
    """,
    response_description="Обновлённая категория в стандартной обёртке API",
    responses={
        200: {
            "description": "Категория успешно обновлена",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 101,
                            "name": "Смартфоны и гаджеты",
                            "description": "Обновлённое описание",
                            "parent_id": None,
                            "manufacturer_id": 3,
                            "images": [
                                {
                                    "upload_id": 10,
                                    "ordering": 0,
                                    "image_url": "https://cdn.example.com/category/smartphones-updated.jpg",
                                }
                            ],
                            "parent": None,
                            "manufacturer": {
                                "id": 3,
                                "name": "Acme Devices",
                                "description": "Мировой производитель электроники"
                            },
                        },
                    }
                }
            },
        },
        400: {
            "description": "Переданы некорректные данные (например, invalid JSON)",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_invalid_image",
                            "message": "Некорректный файл изображения категории",
                            "details": {"reason": "invalid_images_json"},
                        },
                    }
                }
            },
        },
        404: {"description": "Категория не найдена"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("category:update"))],
)
async def update(
    category_id: int,
    name: Annotated[str | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
    parent_id: Annotated[int | None, Form()] = None,
    manufacturer_id: Annotated[int | None, Form()] = None,
    images_json: Annotated[str | None, Form()] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    images_dto = await _build_image_operations_dto(images_json) if images_json else None

    commands = CategoryComposition.build_update_command(db)
    dto = await commands.execute(
        category_id,
        CategoryUpdateDTO(
            name=name,
            description=description,
            parent_id=normalize_optional_fk(parent_id),
            manufacturer_id=normalize_optional_fk(manufacturer_id),
            images=images_dto,
        ),
        user=user,
    )
    return api_response(CategoryReadSchema.model_validate(dto))


@category_commands_router.delete(
    "/{category_id}",
    summary="Удалить категорию",
    description="""
    Удаляет категорию по идентификатору.

    Права:
    - Требуется permission: `category:delete`

    Сценарии:
    - Очистка устаревших категорий.
    - Удаление ошибочно созданной категории.
    """,
    response_description="Флаг успешного удаления",
    responses={
        200: {
            "description": "Категория успешно удалена",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        404: {
            "description": "Категория не найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_not_found",
                            "message": "Категория не найдена",
                            "details": {"category_id": 9999},
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("category:delete"))],
)
async def delete(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = CategoryComposition.build_delete_command(db)
    await commands.execute(category_id, user=user)
    return api_response({"deleted": True})
