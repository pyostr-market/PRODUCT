"""Command endpoints для тегов (запись, с проверкой прав)."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import (
    TagCreateSchema,
    TagUpdateSchema,
    TagReadSchema,
    ProductTagCreateSchema,
    ProductTagReadSchema,
)
from src.catalog.product.application.dto.product import (
    TagCreateDTO,
    TagUpdateDTO,
)
from src.catalog.product.composition import ProductComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

tag_commands_router = APIRouter(
    prefix="/tags",
    tags=["Теги товаров"],
)


# ==================== Tag Commands ====================


@tag_commands_router.post(
    "",
    summary="Создать тег",
    response_model=TagReadSchema,
    dependencies=[Depends(require_permissions("product:create"))],
)
async def create_tag(
    tag_data: TagCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Создать новый тег.

    Требуется право: `product:create`.
    """
    command = ProductComposition.build_create_tag_command(db)
    dto = TagCreateDTO(
        name=tag_data.name,
        description=tag_data.description,
        color=tag_data.color,
    )
    result = await command.execute(dto, user)
    return api_response(TagReadSchema.model_validate(result))


@tag_commands_router.put(
    "/{tag_id}",
    summary="Обновить тег",
    response_model=TagReadSchema,
    dependencies=[Depends(require_permissions("product:update"))],
)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Обновить существующий тег.

    Требуется право: `product:update`.
    """
    command = ProductComposition.build_update_tag_command(db)
    dto = TagUpdateDTO(
        name=tag_data.name,
        description=tag_data.description,
        color=tag_data.color,
    )
    result = await command.execute(tag_id, dto, user)
    return api_response(TagReadSchema.model_validate(result))


@tag_commands_router.delete(
    "/{tag_id}",
    summary="Удалить тег",
    dependencies=[Depends(require_permissions("product:delete"))],
)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Удалить тег.

    Требуется право: `product:delete`.
    """
    command = ProductComposition.build_delete_tag_command(db)
    await command.execute(tag_id, user)
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "Тег удален"},
    )


# ==================== Product-Tag Relations Commands ====================


@tag_commands_router.post(
    "/product-tags",
    summary="Добавить тег к товару",
    response_model=ProductTagReadSchema,
    dependencies=[Depends(require_permissions("product:create"))],
)
async def add_product_tag(
    data: ProductTagCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Добавить тег к товару.

    Требуется право: `product:create`.
    """
    command = ProductComposition.build_add_product_tag_command(db)
    result = await command.execute(
        product_id=data.product_id,
        tag_id=data.tag_id,
        user=user,
    )
    return api_response(ProductTagReadSchema.model_validate(result))


@tag_commands_router.delete(
    "/product-tags/{product_id}/{tag_id}",
    summary="Удалить тег у товара",
    dependencies=[Depends(require_permissions("product:delete"))],
)
async def remove_product_tag(
    product_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Удалить тег у товара.

    Требуется право: `product:delete`.
    """
    command = ProductComposition.build_remove_product_tag_command(db)
    await command.execute(product_id=product_id, tag_id=tag_id, user=user)
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "Тег удален из товара"},
    )
