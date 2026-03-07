from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path
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
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_email_template_queries(db)
    items = await queries.get_all(is_active=True)

    return api_response(
        EmailTemplateListResponse(
            total=len(items),
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
