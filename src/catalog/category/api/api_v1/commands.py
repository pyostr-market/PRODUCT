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
    Создаёт новую категорию с изображениями.

    Права:
    - Требуется permission: `category:create`

    Сценарии:
    - Инициализация новой ветки каталога.
    - Создание категории с привязкой к производителю.
    - Загрузка набора изображений с явным порядком отображения.

    **Формат `images`** (массив объектов с upload_id):
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
            "description": "Некорректные входные данные",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_invalid_image",
                            "message": "Некорректный файл изображения категории",
                            "details": {
                                "reason": "invalid_images",
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
    images_dto = [
        CategoryImageInputDTO(upload_id=img.upload_id, ordering=img.ordering)
        for img in payload.images
    ] if payload.images else []

    commands = CategoryComposition.build_create_command(db)
    dto = await commands.execute(
        CategoryCreateDTO(
            name=payload.name,
            description=payload.description,
            parent_id=normalize_optional_fk(payload.parent_id),
            manufacturer_id=normalize_optional_fk(payload.manufacturer_id),
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
    - Изображения передаются через `images` (JSON-массив операций).
    - Каждая операция имеет поле `action`: `create`, `update`, `delete`, `pass`.
    - `create` — добавить изображение (требуется `upload_id`).
    - `update` — обновить изображение (требуется `upload_id`).
    - `delete` — удалить изображение.
    - `pass` — сохранить существующее изображение (требуется `upload_id`).

    Пример `images`:
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
            "description": "Переданы некорректные данные",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_invalid_image",
                            "message": "Некорректный файл изображения категории",
                            "details": {"reason": "invalid_images"},
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
    images_dto = None
    if payload.images:
        images_dto = [
            CategoryImageOperationDTO(
                action=img.action,
                upload_id=img.upload_id,
                image_url=img.image_url,
                ordering=img.ordering,
            )
            for img in payload.images
        ]

    commands = CategoryComposition.build_update_command(db)
    dto = await commands.execute(
        category_id,
        CategoryUpdateDTO(
            name=payload.name,
            description=payload.description,
            parent_id=normalize_optional_fk(payload.parent_id),
            manufacturer_id=normalize_optional_fk(payload.manufacturer_id),
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
