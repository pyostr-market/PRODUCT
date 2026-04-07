from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import (
    TagCreateSchema,
    TagUpdateSchema,
    TagReadSchema,
    TagListResponse,
    ProductTagCreateSchema,
    ProductTagReadSchema,
    ProductTagListResponse,
)
from src.catalog.product.application.dto.product import (
    TagCreateDTO,
    TagUpdateDTO,
)
from src.catalog.product.application.queries.tag_queries import TagQueries
from src.catalog.product.composition import ProductComposition
from src.catalog.product.infrastructure.models.product_tag import ProductTag
from src.catalog.product.infrastructure.models.tag import Tag
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

tag_router = APIRouter(
    prefix="/tags",
    tags=["Теги товаров"],
)


def _build_tag_queries(db: AsyncSession) -> TagQueries:
    return ProductComposition.build_tag_queries(db)


# ==================== Tag CRUD ====================


@tag_router.post(
    "",
    summary="Создать тег",
    response_model=TagReadSchema,
)
async def create_tag(
    tag_data: TagCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Создать новый тег."""
    command = ProductComposition.build_create_tag_command(db)
    dto = TagCreateDTO(
        name=tag_data.name,
        description=tag_data.description,
    )
    result = await command.execute(dto, user)
    return api_response(TagReadSchema.model_validate(result))


@tag_router.get(
    "",
    summary="Получить все теги",
    response_model=TagListResponse,
)
async def get_all_tags(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Получить список всех тегов с пагинацией."""
    queries = _build_tag_queries(db)
    tags, total = await queries.get_all_tags(limit=limit, offset=offset)
    return api_response(
        TagListResponse(
            total=total,
            items=[TagReadSchema.model_validate(tag) for tag in tags],
        )
    )


@tag_router.get(
    "/{tag_id}",
    summary="Получить тег по ID",
    response_model=TagReadSchema,
)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить тег по ID."""
    queries = _build_tag_queries(db)
    tag = await queries.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Тег не найден")
    return api_response(TagReadSchema.model_validate(tag))


@tag_router.put(
    "/{tag_id}",
    summary="Обновить тег",
    response_model=TagReadSchema,
)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Обновить существующий тег."""
    command = ProductComposition.build_update_tag_command(db)
    dto = TagUpdateDTO(
        name=tag_data.name,
        description=tag_data.description,
    )
    result = await command.execute(tag_id, dto, user)
    return api_response(TagReadSchema.model_validate(result))


@tag_router.delete(
    "/{tag_id}",
    summary="Удалить тег",
)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Удалить тег."""
    command = ProductComposition.build_delete_tag_command(db)
    await command.execute(tag_id, user)
    return JSONResponse(status_code=200, content={"success": True, "message": "Тег удален"})


# ==================== Product-Tag Relations ====================


@tag_router.post(
    "/product-tags",
    summary="Добавить тег к товару",
    response_model=ProductTagReadSchema,

)
async def add_product_tag(
    data: ProductTagCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Добавить тег к товару."""
    command = ProductComposition.build_add_product_tag_command(db)
    result = await command.execute(
        product_id=data.product_id,
        tag_id=data.tag_id,
        user=user,
    )
    return api_response(ProductTagReadSchema.model_validate(result))


@tag_router.delete(
    "/product-tags/{product_id}/{tag_id}",
    summary="Удалить тег у товара",
)
async def remove_product_tag(
    product_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Удалить тег у товара."""
    command = ProductComposition.build_remove_product_tag_command(db)
    await command.execute(product_id=product_id, tag_id=tag_id, user=user)
    return JSONResponse(status_code=200, content={"success": True, "message": "Тег удален из товара"})


@tag_router.get(
    "/product-tags/{product_id}",
    summary="Получить все теги товара",
    response_model=ProductTagListResponse,
)
async def get_product_tags(
    product_id: int,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Получить все теги товара."""
    queries = _build_tag_queries(db)
    product_tags, total = await queries.get_product_tags(product_id=product_id, limit=limit, offset=offset)

    return api_response(
        ProductTagListResponse(
            total=total,
            items=[
                ProductTagReadSchema(
                    id=pt.id,
                    product_id=pt.product_id,
                    tag_id=pt.tag_id,
                    tag=TagReadSchema(
                        tag_id=pt.tag.tag_id,
                        name=pt.tag.name,
                        description=pt.tag.description,
                    ),
                )
                for pt in product_tags
            ],
        )
    )
