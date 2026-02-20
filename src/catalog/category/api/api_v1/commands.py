from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.schemas import CategoryCreateSchema, CategoryReadSchema, CategoryUpdateSchema
from src.catalog.category.application.dto.category import (
    CategoryCreateDTO,
    CategoryImageInputDTO,
    CategoryUpdateDTO,
)
from src.catalog.category.composition import CategoryComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

category_commands_router = APIRouter(tags=["Categories"])


@category_commands_router.post(
    "/",
    status_code=200,
    summary="Создать категорию",
    dependencies=[Depends(require_permissions("category:create"))],
)
async def create(
    payload: CategoryCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = CategoryComposition.build_create_command(db)
    dto = await commands.execute(
        CategoryCreateDTO(
            name=payload.name,
            description=payload.description,
            parent_id=payload.parent_id,
            manufacturer_id=payload.manufacturer_id,
            images=[CategoryImageInputDTO(**image.model_dump()) for image in payload.images],
        ),
        user=user,
    )
    return api_response(CategoryReadSchema.model_validate(dto))


@category_commands_router.put(
    "/{category_id}",
    summary="Обновить категорию",
    dependencies=[Depends(require_permissions("category:update"))],
)
async def update(
    category_id: int,
    payload: CategoryUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = CategoryComposition.build_update_command(db)
    dto = await commands.execute(
        category_id,
        CategoryUpdateDTO(
            name=payload.name,
            description=payload.description,
            parent_id=payload.parent_id,
            manufacturer_id=payload.manufacturer_id,
            images=(
                [CategoryImageInputDTO(**image.model_dump()) for image in payload.images]
                if payload.images is not None
                else None
            ),
        ),
        user=user,
    )
    return api_response(CategoryReadSchema.model_validate(dto))


@category_commands_router.delete(
    "/{category_id}",
    summary="Удалить категорию",
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
