from typing import List

from fastapi import APIRouter, Depends, HTTPException
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
from src.catalog.product.application.commands.create_tag import CreateTagCommand
from src.catalog.product.application.commands.update_tag import UpdateTagCommand
from src.catalog.product.application.commands.delete_tag import DeleteTagCommand
from src.catalog.product.application.commands.product_tag_commands import (
    AddProductTagCommand,
    RemoveProductTagCommand,
)
from src.catalog.product.application.dto.product import (
    TagCreateDTO,
    TagUpdateDTO,
)
from src.catalog.product.application.queries.tag_queries import TagQueries
from src.catalog.product.infrastructure.models.product_tag import ProductTag
from src.catalog.product.infrastructure.models.tag import Tag
from src.core.api.responses import api_response
from src.core.db.database import get_db

tag_router = APIRouter(
    prefix="/tags",
    tags=["Теги товаров"],
)


# ==================== Tag CRUD ====================


@tag_router.post(
    "",
    summary="Создать тег",
    response_model=TagReadSchema,
)
async def create_tag(
    tag_data: TagCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    """Создать новый тег."""
    command = ProductComposition.build_create_tag_command(db)
    dto = TagCreateDTO(
        name=tag_data.name,
        description=tag_data.description,
    )
    result = await command.execute(dto)
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
    queries = TagQueries(db=db)
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
    queries = TagQueries(db=db)
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
):
    """Обновить существующий тег."""
    command = ProductComposition.build_update_tag_command(db)
    dto = TagUpdateDTO(
        name=tag_data.name,
        description=tag_data.description,
    )
    result = await command.execute(tag_id, dto)
    return api_response(TagReadSchema.model_validate(result))


@tag_router.delete(
    "/{tag_id}",
    summary="Удалить тег",
)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удалить тег."""
    command = ProductComposition.build_delete_tag_command(db)
    await command.execute(tag_id)
    return api_response(None, message="Тег удален")


# ==================== Product-Tag Relations ====================


@tag_router.post(
    "/product-tags",
    summary="Добавить тег к товару",
    response_model=ProductTagReadSchema,
)
async def add_product_tag(
    data: ProductTagCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    """Добавить тег к товару."""
    command = AddProductTagCommand(db=db)
    await command.execute(product_id=data.product_id, tag_id=data.tag_id)
    await db.commit()

    # Возвращаем созданную связь
    stmt = (
        select(ProductTag, Tag)
        .join(Tag, Tag.id == ProductTag.tag_id)
        .where(
            ProductTag.product_id == data.product_id,
            ProductTag.tag_id == data.tag_id,
        )
    )
    result = await db.execute(stmt)
    product_tag_row = result.first()
    
    if product_tag_row:
        product_tag, tag = product_tag_row
        return api_response(
            ProductTagReadSchema(
                id=product_tag.id,
                product_id=product_tag.product_id,
                tag_id=product_tag.tag_id,
                tag=TagReadSchema(
                    tag_id=tag.id,
                    name=tag.name,
                    description=tag.description,
                ),
            )
        )
    return api_response(None)


@tag_router.delete(
    "/product-tags/{product_id}/{tag_id}",
    summary="Удалить тег у товара",
)
async def remove_product_tag(
    product_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Удалить тег у товара."""
    command = RemoveProductTagCommand(db=db)
    await command.execute(product_id=product_id, tag_id=tag_id)
    await db.commit()
    return api_response(None, message="Тег удален из товара")


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
    queries = TagQueries(db=db)
    tags, total = await queries.get_product_tags(product_id=product_id, limit=limit, offset=offset)
    
    # Получаем详细信息 о тегах с информацией о связи
    stmt = (
        select(ProductTag, Tag)
        .join(Tag, Tag.id == ProductTag.tag_id)
        .where(ProductTag.product_id == product_id)
        .order_by(ProductTag.id)
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    product_tags = result.all()
    
    return api_response(
        ProductTagListResponse(
            total=total,
            items=[
                ProductTagReadSchema(
                    id=pt.id,
                    product_id=pt.product_id,
                    tag_id=pt.tag_id,
                    tag=TagReadSchema(
                        tag_id=tag.id,
                        name=tag.name,
                        description=tag.description,
                    ),
                )
                for pt, tag in product_tags
            ],
        )
    )
