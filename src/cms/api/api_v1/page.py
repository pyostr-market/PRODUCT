from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.cms.api.schemas.page_schemas import (
    AddBlockSchema,
    PageBlockReadSchema,
    PageCreateSchema,
    PageListResponse,
    PageReadSchema,
    PageUpdateSchema,
)
from src.cms.application.commands.add_page_block import AddPageBlockCommand
from src.cms.application.commands.create_page import CreatePageCommand
from src.cms.application.commands.delete_page import DeletePageCommand
from src.cms.application.commands.update_page import UpdatePageCommand
from src.cms.application.dto.cms_dto import PageBlockDTO, PageCreateDTO, PageUpdateDTO
from src.cms.application.queries.page_queries import PageQueries
from src.cms.composition import CmsComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

page_router = APIRouter(tags=["CMS: Pages"])


# Admin endpoints - должны быть зарегистрированы ПЕРЕД public endpoints
@page_router.post(
    "/admin",
    summary="Создать страницу (admin)",
    response_description="Созданная страница",
)
async def create_page(
    schema: PageCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_create_page_command(db)
    
    # Конвертируем блоки из schema в DTO
    blocks_dto = None
    if schema.blocks:
        blocks_dto = [
            PageBlockDTO(
                block_type=b.block_type,
                data=b.data,
                order=b.order,
            )
            for b in schema.blocks
        ]
    
    dto = PageCreateDTO(
        slug=schema.slug,
        title=schema.title,
        is_published=schema.is_published,
        blocks=blocks_dto,
    )
    result = await command.execute(dto)

    return api_response(PageReadSchema.model_validate(result))


@page_router.put(
    "/admin/{page_id}",
    summary="Обновить страницу (admin)",
    response_description="Обновленная страница",
)
async def update_page(
    page_id: int,
    schema: PageUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_update_page_command(db)
    dto = PageUpdateDTO(
        slug=schema.slug,
        title=schema.title,
        is_published=schema.is_published,
    )
    result = await command.execute(page_id, dto)

    return api_response(PageReadSchema.model_validate(result))


@page_router.delete(
    "/admin/{page_id}",
    summary="Удалить страницу (admin)",
    response_description="Результат удаления",
)
async def delete_page(
    page_id: int,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_delete_page_command(db)
    result = await command.execute(page_id)

    return api_response({"success": result, "page_id": page_id})


@page_router.post(
    "/admin/{page_id}/blocks",
    summary="Добавить блок на страницу (admin)",
    response_description="ID добавленного блока",
)
async def add_page_block(
    page_id: int,
    schema: AddBlockSchema,
    db: AsyncSession = Depends(get_db),
):
    command = CmsComposition.build_add_page_block_command(db)
    block_id = await command.execute(
        page_id=page_id,
        block_type=schema.block_type,
        data=schema.data,
        order=schema.order,
    )

    return api_response({"block_id": block_id, "page_id": page_id})


# Public endpoints
@page_router.get(
    "/{slug}",
    summary="Получить страницу по slug",
    response_description="Страница с блоками",
)
async def get_page(
    slug: str = Path(..., description="URL идентификатор страницы"),
    db: AsyncSession = Depends(get_db),
):
    queries = CmsComposition.build_page_queries(db)
    result = await queries.get_by_slug(slug)

    if not result:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": {"message": "Страница не найдена", "code": "page_not_found"}}
        )

    return api_response(PageReadSchema.model_validate(result))
