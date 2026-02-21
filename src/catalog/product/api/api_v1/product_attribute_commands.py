from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import (
    ProductAttributeCreateSchema,
    ProductAttributeReadSchema,
    ProductAttributeUpdateSchema,
)
from src.catalog.product.composition import ProductComposition
from src.catalog.product.domain.aggregates.product import ProductAttributeAggregate
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

product_attribute_commands_router = APIRouter(
    tags=["Атрибуты продуктов"],
)


# CREATE
@product_attribute_commands_router.post(
    "/attribute",
    status_code=200,
    summary="Создать атрибут продукта",
    description="""
    Создаёт новый атрибут продукта.

    Права:
    - Требуется permission: `product_attribute:create`

    Сценарии:
    - Добавление нового атрибута для фильтрации товаров.
    - Создание атрибута для характеристики товаров.
    """,
    response_description="Созданный атрибут продукта в стандартной обёртке API",
    responses={
        200: {
            "description": "Атрибут продукта успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 10,
                            "name": "RAM",
                            "value": "",
                            "is_filterable": True,
                        },
                    }
                }
            },
        },
        400: {"description": "Некорректные данные (имя слишком короткое)"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Атрибут продукта уже существует"},
    },
    dependencies=[Depends(require_permissions("product_attribute:create"))],
)
async def create_product_attribute(
    payload: ProductAttributeCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_create_product_attribute_command(db)

    dto = await commands.execute(
        ProductAttributeAggregate(
            name=payload.name,
            value=payload.value,
            is_filterable=payload.is_filterable,
        ),
        user=user,
    )

    return api_response(
        ProductAttributeReadSchema.model_validate(dto)
    )


# UPDATE
@product_attribute_commands_router.put(
    "/attribute/{attribute_id}",
    summary="Обновить атрибут продукта",
    description="""
    Обновляет существующий атрибут продукта.

    Права:
    - Требуется permission: `product_attribute:update`

    Сценарии:
    - Переименование атрибута.
    - Изменение флага is_filterable.
    """,
    response_description="Обновлённый атрибут продукта в стандартной обёртке API",
    responses={
        200: {
            "description": "Атрибут продукта успешно обновлён",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 10,
                            "name": "Оперативная память",
                            "value": "",
                            "is_filterable": True,
                        },
                    }
                }
            },
        },
        400: {"description": "Имя слишком короткое"},
        404: {"description": "Атрибут продукта не найден"},
        403: {"description": "Недостаточно прав"},
        409: {"description": "Конфликт уникальности имени"},
    },
    dependencies=[Depends(require_permissions("product_attribute:update"))],
)
async def update_product_attribute(
    attribute_id: int,
    payload: ProductAttributeUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_update_product_attribute_command(db)

    dto = await commands.execute(
        attribute_id,
        ProductAttributeAggregate(
            name=payload.name,
            value=payload.value,
            is_filterable=payload.is_filterable,
        ),
        user=user,
    )

    return api_response(
        ProductAttributeReadSchema.model_validate(dto)
    )


# DELETE
@product_attribute_commands_router.delete(
    "/attribute/{attribute_id}",
    summary="Удалить атрибут продукта",
    description="""
    Удаляет атрибут продукта по ID.

    Права:
    - Требуется permission: `product_attribute:delete`

    Сценарии:
    - Удаление неактуального атрибута.
    - Очистка ошибочно созданной записи.
    """,
    responses={
        200: {
            "description": "Атрибут продукта успешно удалён",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        404: {"description": "Атрибут продукта не найден"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("product_attribute:delete"))],
)
async def delete_product_attribute(
    attribute_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_delete_product_attribute_command(db)
    await commands.execute(
        attribute_id,
        user=user,
    )

    return api_response({"deleted": True})
