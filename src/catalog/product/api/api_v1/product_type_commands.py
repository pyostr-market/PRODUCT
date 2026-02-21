from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.product_type import (
    ProductTypeCreateSchema,
    ProductTypeReadSchema,
    ProductTypeUpdateSchema,
)
from src.catalog.product.application.dto.product_type import (
    ProductTypeCreateDTO,
    ProductTypeUpdateDTO,
)
from src.catalog.product.composition import ProductComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

product_type_commands_router = APIRouter(
    tags=["Типы продуктов"],
)


# CREATE
@product_type_commands_router.post(
    "/type",
    status_code=200,
    summary="Создать тип продукта",
    description="""
    Создаёт новый тип продукта.

    Права:
    - Требуется permission: `product_type:create`

    Сценарии:
    - Добавление нового типа продукта в справочник.
    - Подготовка данных для привязки товаров к типу.
    """,
    response_description="Созданный тип продукта в стандартной обёртке API",
    responses={
        200: {
            "description": "Тип продукта успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 5,
                            "name": "Смартфоны",
                            "parent_id": None,
                        },
                    }
                }
            },
        },
        400: {"description": "Некорректные данные (имя слишком короткое)"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Тип продукта уже существует"},
    },
    dependencies=[Depends(require_permissions("product_type:create"))],
)
async def create_product_type(
    payload: ProductTypeCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_create_product_type_command(db)

    dto = await commands.execute(
        ProductTypeCreateDTO(**payload.model_dump()),
        user=user,
    )

    return api_response(
        ProductTypeReadSchema.model_validate(dto)
    )


# UPDATE
@product_type_commands_router.put(
    "/type/{product_type_id}",
    summary="Обновить тип продукта",
    description="""
    Обновляет существующий тип продукта.

    Права:
    - Требуется permission: `product_type:update`

    Сценарии:
    - Переименование типа продукта.
    - Изменение родительской категории типа.
    """,
    response_description="Обновлённый тип продукта в стандартной обёртке API",
    responses={
        200: {
            "description": "Тип продукта успешно обновлён",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 5,
                            "name": "Смартфоны Pro",
                            "parent_id": None,
                        },
                    }
                }
            },
        },
        400: {"description": "Имя слишком короткое"},
        404: {"description": "Тип продукта не найден"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Конфликт уникальности имени"},
    },
    dependencies=[Depends(require_permissions("product_type:update"))],
)
async def update_product_type(
    product_type_id: int,
    payload: ProductTypeUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_update_product_type_command(db)

    dto = await commands.execute(
        product_type_id,
        ProductTypeUpdateDTO(**payload.model_dump()),
        user=user,
    )

    return api_response(
        ProductTypeReadSchema.model_validate(dto)
    )


# DELETE
@product_type_commands_router.delete(
    "/type/{product_type_id}",
    summary="Удалить тип продукта",
    description="""
    Удаляет тип продукта по ID.

    Права:
    - Требуется permission: `product_type:delete`

    Сценарии:
    - Удаление неактуального типа продукта.
    - Очистка ошибочно созданной записи.
    """,
    responses={
        200: {
            "description": "Тип продукта успешно удалён",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        404: {"description": "Тип продукта не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("product_type:delete"))],
)
async def delete_product_type(
    product_type_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_delete_product_type_command(db)
    await commands.execute(
        product_type_id,
        user=user,
    )

    return api_response({"deleted": True})
