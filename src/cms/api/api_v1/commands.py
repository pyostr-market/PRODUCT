from typing import Any, List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.page_schemas import (
    AddBlockSchema,
    PageCreateSchema,
    PageReadSchema,
    PageUpdateSchema,
)
from src.cms.application.commands.add_page_block import AddPageBlockCommand
from src.cms.application.commands.create_page import CreatePageCommand
from src.cms.application.commands.delete_page import DeletePageCommand
from src.cms.application.commands.update_page import UpdatePageCommand
from src.cms.application.dto.cms_dto import PageBlockDTO, PageCreateDTO, PageUpdateDTO
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

page_commands_router = APIRouter(
    tags=["CMS: Pages"],
)


def _page_create_schema_to_dto(schema: PageCreateSchema) -> PageCreateDTO:
    """Конвертация схемы создания страницы в DTO."""
    blocks_dto = []
    if schema.blocks:
        for block in schema.blocks:
            blocks_dto.append(
                PageBlockDTO(
                    block_type=block.block_type,
                    data=block.data,
                    order=block.order,
                )
            )
    return PageCreateDTO(
        slug=schema.slug,
        title=schema.title,
        is_published=schema.is_published,
        blocks=blocks_dto,
    )


def _page_update_schema_to_dto(schema: PageUpdateSchema) -> PageUpdateDTO:
    """Конвертация схемы обновления страницы в DTO."""
    return PageUpdateDTO(
        slug=schema.slug,
        title=schema.title,
        is_published=schema.is_published,
    )


@page_commands_router.post(
    "",
    status_code=200,
    summary="Создать страницу",
    description="""
    Создаёт новую страницу с блоками контента.

    Права:
    - Требуется permission: `cms:create`

    Сценарии:
    - Создание новой статической страницы (о компании, доставка, контакты).
    - Создание лендинга с набором блоков.
    - Публикация новой страницы с предварительной настройкой блоков.

    **Формат `blocks`** (массив объектов с block_type и data):
    ```json
    [
      {"block_type": "text", "data": {"content": "Добро пожаловать"}, "order": 0},
      {"block_type": "image", "data": {"upload_id": 1, "alt": "Баннер"}, "order": 1},
      {"block_type": "html", "data": {"html": "<div>Custom HTML</div>"}, "order": 2}
    ]
    ```

    Каждый элемент массива содержит:
    - `block_type`: тип блока (text, image, video, html, etc.)
    - `data`: данные блока (зависит от типа)
    - `order`: порядок сортировки (int)

    **Типы блоков:**
    - `text` — текстовый блок с контентом
    - `image` — изображение с upload_id и alt
    - `video` — видео с URL или upload_id
    - `html` — произвольный HTML
    - `accordion` — аккордеон с вопросами и ответами
    - `features` — список преимуществ
    """,
    response_description="Созданная страница в стандартной обёртке API",
    responses={
        200: {
            "description": "Страница успешно создана",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "slug": "about-us",
                            "title": "О компании",
                            "is_published": False,
                            "blocks": [
                                {
                                    "id": 1,
                                    "page_id": 1,
                                    "block_type": "text",
                                    "order": 0,
                                    "data": {"content": "Добро пожаловать"},
                                    "is_active": True,
                                },
                                {
                                    "id": 2,
                                    "page_id": 1,
                                    "block_type": "image",
                                    "order": 1,
                                    "data": {"upload_id": 1, "alt": "Баннер"},
                                    "is_active": True,
                                },
                            ],
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
                            "code": "cms_invalid_data",
                            "message": "Некорректные данные CMS",
                            "details": {
                                "reason": "invalid_data",
                            },
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
        409: {
            "description": "Slug уже существует",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "page_slug_already_exists",
                            "message": "Страница с таким slug уже существует",
                            "details": {"slug": "about-us"},
                        },
                    }
                }
            },
        },
    },
    dependencies=[Depends(require_permissions("cms:create"))],
)
async def create(
    schema: PageCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dto = _page_create_schema_to_dto(schema)
    commands = CmsComposition.build_create_page_command(db)
    result = await commands.execute(dto)
    return api_response(PageReadSchema.model_validate(result))


@page_commands_router.put(
    "/{page_id}",
    summary="Обновить страницу",
    description="""
    Частично обновляет страницу по идентификатору.

    Права:
    - Требуется permission: `cms:update`

    Сценарии:
    - Изменение заголовка или slug страницы.
    - Публикация или снятие с публикации.
    - Управление блоками контента.

    Работа с блоками:
    - Блоки передаются через `blocks` (массив операций).
    - Каждая операция имеет поле `action`: `create`, `update`, `delete`, `pass`.
    - `create` — добавить блок (требуется `block_type`).
    - `update` — обновить блок (требуется `block_id`).
    - `delete` — удалить блок (требуется `block_id`).
    - `pass` — сохранить существующий блок (требуется `block_id`).

    Пример `blocks`:
    ```json
    [
      {"action": "pass", "block_id": 1, "order": 0},
      {"action": "update", "block_id": 2, "data": {"content": "Новый текст"}, "order": 1},
      {"action": "delete", "block_id": 3},
      {"action": "create", "block_type": "text", "data": {"content": "Новый блок"}, "order": 2}
    ]
    ```
    """,
    response_description="Обновлённая страница в стандартной обёртке API",
    responses={
        200: {
            "description": "Страница успешно обновлена",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "slug": "about-us-updated",
                            "title": "О компании (обновлено)",
                            "is_published": True,
                            "blocks": [
                                {
                                    "id": 1,
                                    "page_id": 1,
                                    "block_type": "text",
                                    "order": 0,
                                    "data": {"content": "Добро пожаловать"},
                                    "is_active": True,
                                },
                            ],
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
                            "code": "cms_invalid_data",
                            "message": "Некорректные данные CMS",
                            "details": {"reason": "invalid_data"},
                        },
                    }
                }
            },
        },
        404: {
            "description": "Страница не найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "page_not_found",
                            "message": "Страница не найдена",
                            "details": {"page_id": 9999},
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
        409: {
            "description": "Slug уже существует",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "page_slug_already_exists",
                            "message": "Страница с таким slug уже существует",
                            "details": {"slug": "about-us"},
                        },
                    }
                }
            },
        },
    },
    dependencies=[Depends(require_permissions("cms:update"))],
)
async def update(
    page_id: int,
    schema: PageUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    dto = _page_update_schema_to_dto(schema)
    commands = CmsComposition.build_update_page_command(db)
    result = await commands.execute(page_id, dto)
    return api_response(PageReadSchema.model_validate(result))


@page_commands_router.delete(
    "/{page_id}",
    summary="Удалить страницу",
    description="""
    Удаляет страницу по идентификатору.

    Права:
    - Требуется permission: `cms:delete`

    Сценарии:
    - Удаление устаревшей страницы.
    - Удаление ошибочно созданной страницы.
    """,
    response_description="Флаг успешного удаления",
    responses={
        200: {
            "description": "Страница успешно удалена",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"page_id": 1, "deleted": True}}
                }
            },
        },
        404: {
            "description": "Страница не найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "page_not_found",
                            "message": "Страница не найдена",
                            "details": {"page_id": 9999},
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("cms:delete"))],
)
async def delete(
    page_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = CmsComposition.build_delete_page_command(db)
    result = await commands.execute(page_id)
    return api_response({"page_id": page_id, "deleted": result})


@page_commands_router.post(
    "/{page_id}/blocks",
    summary="Добавить блок на страницу",
    description="""
    Добавляет новый блок контента на существующую страницу.

    Права:
    - Требуется permission: `cms:update`

    Сценарии:
    - Добавление нового текстового блока.
    - Добавление изображения или видео.
    - Расширение контента страницы.

    **Формат `data`**:
    ```json
    {"content": "Текст блока"}
    ```
    или для изображения:
    ```json
    {"upload_id": 1, "alt": "Описание изображения"}
    ```
    """,
    response_description="ID добавленного блока",
    responses={
        200: {
            "description": "Блок успешно добавлен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "block_id": 5,
                            "page_id": 1,
                        },
                    }
                }
            },
        },
        404: {
            "description": "Страница не найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "page_not_found",
                            "message": "Страница не найдена",
                            "details": {"page_id": 9999},
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("cms:update"))],
)
async def add_block(
    page_id: int,
    schema: AddBlockSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = CmsComposition.build_add_page_block_command(db)
    block_id = await commands.execute(
        page_id=page_id,
        block_type=schema.block_type,
        data=schema.data,
        order=schema.order,
    )
    return api_response({"block_id": block_id, "page_id": page_id})
