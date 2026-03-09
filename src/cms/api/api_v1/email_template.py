from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.email_template_schemas import (
    EmailTemplateCreateSchema,
    EmailTemplateListResponse,
    EmailTemplateReadSchema,
    EmailTemplateUpdateSchema,
)
from src.cms.application.commands.create_email_template import CreateEmailTemplateCommand
from src.cms.application.commands.delete_email_template import DeleteEmailTemplateCommand
from src.cms.application.commands.update_email_template import UpdateEmailTemplateCommand
from src.cms.application.dto.cms_dto import EmailTemplateCreateDTO, EmailTemplateUpdateDTO
from src.cms.application.queries.email_template_queries import EmailTemplateQueries
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

email_template_router = APIRouter(tags=["CMS: Email Templates"])


# Admin endpoints - должны быть зарегистрированы ПЕРЕД public endpoints
@email_template_router.post(
    "/admin",
    summary="Создать email шаблон (admin)",
    description="""
    Создаёт новый email шаблон.

    Права:
    - Требуется permission: `cms:create`

    Сценарии:
    - Создание шаблона для транзакционных писем.
    - Настройка email уведомлений.
    """,
    response_description="Созданный шаблон",
    responses={
        200: {"description": "Шаблон успешно создан"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Шаблон с таким key уже существует"},
    },
    dependencies=[Depends(require_permissions("cms:create"))],
)
async def create_template(
    schema: EmailTemplateCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_create_email_template_command(db)
    dto = EmailTemplateCreateDTO(
        key=schema.key,
        subject=schema.subject,
        body_html=schema.body_html,
        body_text=schema.body_text,
        variables=schema.variables,
        is_active=schema.is_active,
    )
    result = await command.execute(dto)

    return api_response(EmailTemplateReadSchema.model_validate(result))


@email_template_router.put(
    "/admin/{template_id}",
    summary="Обновить email шаблон (admin)",
    description="""
    Обновляет email шаблон по идентификатору.

    Права:
    - Требуется permission: `cms:update`

    Сценарии:
    - Изменение текста или темы письма.
    - Обновление переменных шаблона.
    """,
    response_description="Обновленный шаблон",
    responses={
        200: {"description": "Шаблон успешно обновлен"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Шаблон не найден"},
    },
    dependencies=[Depends(require_permissions("cms:update"))],
)
async def update_template(
    template_id: int,
    schema: EmailTemplateUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_update_email_template_command(db)
    dto = EmailTemplateUpdateDTO(
        subject=schema.subject,
        body_html=schema.body_html,
        body_text=schema.body_text,
        variables=schema.variables,
        is_active=schema.is_active,
    )
    result = await command.execute(template_id, dto)

    return api_response(EmailTemplateReadSchema.model_validate(result))


@email_template_router.delete(
    "/admin/{template_id}",
    summary="Удалить email шаблон (admin)",
    description="""
    Удаляет email шаблон по идентификатору.

    Права:
    - Требуется permission: `cms:delete`

    Сценарии:
    - Удаление устаревшего шаблона.
    """,
    response_description="Результат удаления",
    responses={
        200: {"description": "Шаблон успешно удален"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Шаблон не найден"},
    },
    dependencies=[Depends(require_permissions("cms:delete"))],
)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_delete_email_template_command(db)
    result = await command.execute(template_id)

    return api_response({"success": result, "template_id": template_id})


@email_template_router.get(
    "/admin/{template_id}",
    summary="Получить email шаблон по ID (admin)",
    description="""
    Возвращает детальную информацию о email шаблоне по идентификатору.

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Получение шаблона для админки.
    """,
    response_description="Email шаблон",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def get_template_by_id(
    template_id: int = Path(..., description="ID шаблона"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_email_template_queries(db)
    result = await queries.get_by_id(template_id)

    if not result:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"message": "Шаблон не найден", "code": "email_template_not_found"}}
        )

    return api_response(EmailTemplateReadSchema.model_validate(result))


@email_template_router.get(
    "/admin/search",
    summary="Поиск email шаблонов (admin)",
    description="""
    Поиск email шаблонов по частичному совпадению в key или subject (LIKE).

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Поиск шаблонов в админке.
    """,
    response_description="Список шаблонов",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def search_templates(
    q: Optional[str] = Query(None, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_email_template_queries(db)
    items, total = await queries.search(query=q or "", limit=limit, offset=offset)

    return api_response(
        EmailTemplateListResponse(
            total=total,
            items=[EmailTemplateReadSchema.model_validate(i) for i in items],
        )
    )


@email_template_router.get(
    "/admin",
    summary="Получить все email шаблоны (admin)",
    description="""
    Возвращает список всех email шаблонов с пагинацией.

    Права:
    - Требуется permission: `cms:view`

    Сценарии:
    - Управление шаблонами в админке.
    """,
    response_description="Список шаблонов",
    dependencies=[Depends(require_permissions("cms:view"))],
)
async def get_all_templates_admin(
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_email_template_queries(db)
    items, total = await queries.filter(is_active=None, limit=limit, offset=offset)

    return api_response(
        EmailTemplateListResponse(
            total=total,
            items=[EmailTemplateReadSchema.model_validate(i) for i in items],
        )
    )


# Public endpoints
@email_template_router.get(
    "",
    summary="Получить все email шаблоны",
    description="""
    Возвращает список активных email шаблонов.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам).

    Сценарии:
    - Получение списка доступных шаблонов.
    """,
    response_description="Список шаблонов",
)
async def get_all_templates(
    limit: int = Query(10, ge=1, le=100, description="Лимит записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_email_template_queries(db)
    items, total = await queries.filter(is_active=True, limit=limit, offset=offset)

    return api_response(
        EmailTemplateListResponse(
            total=total,
            items=[EmailTemplateReadSchema.model_validate(i) for i in items],
        )
    )


@email_template_router.get(
    "/{key}",
    summary="Получить шаблон по ключу",
    description="""
    Возвращает email шаблон по ключу.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам).

    Сценарии:
    - Получение шаблона для отправки письма.
    """,
    response_description="Email шаблон",
    responses={
        200: {"description": "Шаблон успешно получен"},
        404: {"description": "Шаблон не найден"},
    },
)
async def get_template(
    key: str = Path(..., description="Ключ шаблона"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_email_template_queries(db)
    result = await queries.get_by_key(key)

    if not result:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"message": "Шаблон не найден", "code": "email_template_not_found"}}
        )

    return api_response(EmailTemplateReadSchema.model_validate(result))
