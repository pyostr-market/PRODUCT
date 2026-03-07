from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.faq_schemas import (
    FaqCategoryListResponse,
    FaqCreateSchema,
    FaqListResponse,
    FaqReadSchema,
    FaqUpdateSchema,
)
from src.cms.application.commands.create_faq import CreateFaqCommand
from src.cms.application.commands.delete_faq import DeleteFaqCommand
from src.cms.application.commands.update_faq import UpdateFaqCommand
from src.cms.application.dto.cms_dto import FaqCreateDTO, FaqUpdateDTO
from src.cms.application.queries.faq_queries import FaqQueries
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

faq_router = APIRouter(tags=["CMS: FAQ"])


# Admin endpoints - должны быть зарегистрированы ПЕРЕД public endpoints
@faq_router.post(
    "/admin",
    summary="Создать FAQ (admin)",
    description="""
    Создаёт новый FAQ элемент.

    Права:
    - Требуется permission: `cms:create`

    Сценарии:
    - Добавление нового вопроса и ответа.
    - Создание FAQ с категоризацией.
    """,
    response_description="Созданный FAQ",
    responses={
        200: {"description": "FAQ успешно создан"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("cms:create"))],
)
async def create_faq(
    schema: FaqCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_create_faq_command(db)
    dto = FaqCreateDTO(
        question=schema.question,
        answer=schema.answer,
        category=schema.category,
        order=schema.order,
        is_active=schema.is_active,
    )
    result = await command.execute(dto)

    return api_response(FaqReadSchema.model_validate(result))


@faq_router.put(
    "/admin/{faq_id}",
    summary="Обновить FAQ (admin)",
    description="""
    Обновляет FAQ элемент по идентификатору.

    Права:
    - Требуется permission: `cms:update`

    Сценарии:
    - Изменение вопроса или ответа.
    - Обновление категории или порядка.
    """,
    response_description="Обновленный FAQ",
    responses={
        200: {"description": "FAQ успешно обновлен"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "FAQ не найден"},
    },
    dependencies=[Depends(require_permissions("cms:update"))],
)
async def update_faq(
    faq_id: int,
    schema: FaqUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_update_faq_command(db)
    dto = FaqUpdateDTO(
        question=schema.question,
        answer=schema.answer,
        category=schema.category,
        order=schema.order,
        is_active=schema.is_active,
    )
    result = await command.execute(faq_id, dto)

    return api_response(FaqReadSchema.model_validate(result))


@faq_router.delete(
    "/admin/{faq_id}",
    summary="Удалить FAQ (admin)",
    description="""
    Удаляет FAQ элемент по идентификатору.

    Права:
    - Требуется permission: `cms:delete`

    Сценарии:
    - Удаление устаревшего FAQ.
    """,
    response_description="Результат удаления",
    responses={
        200: {"description": "FAQ успешно удален"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "FAQ не найден"},
    },
    dependencies=[Depends(require_permissions("cms:delete"))],
)
async def delete_faq(
    faq_id: int,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_delete_faq_command(db)
    result = await command.execute(faq_id)

    return api_response({"success": result, "faq_id": faq_id})


# Public endpoints
@faq_router.get(
    "",
    summary="Получить все FAQ",
    description="""
    Возвращает список опубликованных FAQ.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам).

    Сценарии:
    - Отображение FAQ на сайте.
    - Фильтрация по категории.
    """,
    response_description="Список FAQ",
)
async def get_all_faq(
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_faq_queries(db)
    items = await queries.get_all(category=category, is_active=True)

    return api_response(
        FaqListResponse(
            total=len(items),
            items=[FaqReadSchema.model_validate(i) for i in items],
        )
    )


@faq_router.get(
    "/categories",
    summary="Получить категории FAQ",
    description="""
    Возвращает список всех категорий FAQ.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам).
    """,
    response_description="Список категорий",
)
async def get_faq_categories(
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_faq_queries(db)
    categories = await queries.get_categories()

    return api_response(FaqCategoryListResponse(categories=categories))
