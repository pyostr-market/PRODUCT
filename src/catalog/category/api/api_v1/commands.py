from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.schemas import (
    CategoryCreateSchema,
    CategoryReadSchema,
    CategoryUpdateSchema,
)
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


@category_commands_router.post(
    "",
    status_code=200,
    summary="Создать категорию",
    description="""
    Создаёт новую категорию с изображением.

    Права:
    - Требуется permission: `category:create`

    Сценарии:
    - Инициализация новой ветки каталога.
    - Создание категории с привязкой к производителю.
    - Загрузка изображения категории.

    **Формат `image`** (объект с upload_id):
    ```json
    {"upload_id": 1}
    ```

    Где:
    - `upload_id`: ID предварительно загруженного изображения через UploadHistory
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
                            "image": {
                                "upload_id": 10,
                                "image_url": "https://cdn.example.com/category/smartphones-main.jpg",
                            },
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
            "description": "Некорректные входные данные",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_invalid_image",
                            "message": "Некорректный файл изображения категории",
                            "details": {
                                "reason": "invalid_image",
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
    payload: CategoryCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    image_dto = None
    if payload.image:
        image_dto = CategoryImageInputDTO(upload_id=payload.image.upload_id)

    commands = CategoryComposition.build_create_command(db)
    dto = await commands.execute(
        CategoryCreateDTO(
            name=payload.name,
            description=payload.description,
            parent_id=normalize_optional_fk(payload.parent_id),
            manufacturer_id=normalize_optional_fk(payload.manufacturer_id),
            image=image_dto,
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
    - Обновление изображения категории.

    Работа с изображением:
    - Изображение передаётся через `image` (JSON-объект операции).
    - Операция имеет поле `action`: `create`, `update`, `delete`, `pass`.
    - `create` — добавить изображение (требуется `upload_id`).
    - `update` — обновить изображение (требуется `upload_id`).
    - `delete` — удалить изображение.
    - `pass` — сохранить существующее изображение (требуется `upload_id`).

    Пример `image`:
    ```json
    {"action": "create", "upload_id": 789}
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
                            "image": {
                                "upload_id": 10,
                                "image_url": "https://cdn.example.com/category/smartphones-updated.jpg",
                            },
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
            "description": "Переданы некорректные данные",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_invalid_image",
                            "message": "Некорректный файл изображения категории",
                            "details": {"reason": "invalid_image"},
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
    payload: CategoryUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    print(payload)
    image_dto = None
    if payload.image:
        image_dto = CategoryImageOperationDTO(
            action=payload.image.action,
            upload_id=payload.image.upload_id,
            image_url=payload.image.image_url,
        )

    commands = CategoryComposition.build_update_command(db)
    dto = await commands.execute(
        category_id,
        CategoryUpdateDTO(
            name=payload.name,
            description=payload.description,
            parent_id=normalize_optional_fk(payload.parent_id),
            manufacturer_id=normalize_optional_fk(payload.manufacturer_id),
            image=image_dto,
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
