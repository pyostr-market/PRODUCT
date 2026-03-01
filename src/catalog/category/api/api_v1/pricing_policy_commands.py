from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.schemas import (
    CategoryPricingPolicyCreateSchema,
    CategoryPricingPolicyReadSchema,
    CategoryPricingPolicyUpdateSchema,
)
from src.catalog.category.application.dto.pricing_policy import (
    CategoryPricingPolicyCreateDTO,
    CategoryPricingPolicyUpdateDTO,
)
from src.catalog.category.composition import CategoryPricingPolicyComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

category_pricing_policy_commands_router = APIRouter(
    tags=["Тарификация категории"],
)


# CREATE
@category_pricing_policy_commands_router.post(
    "",
    status_code=200,
    summary="Создать политику ценообразования категории",
    description="""
    Создаёт новую политику ценообразования для категории.

    Права:
    - Требуется permission: `category_pricing_policy:create`

    Сценарии:
    - Настройка ценообразования для новой категории.
    - Установка наценок, комиссий и налогов для категории.

    Поля:
    - `category_id`: ID категории (обязательно, уникальное значение)
    - `markup_fixed`: Фиксированная наценка (опционально)
    - `markup_percent`: Наценка в процентах (опционально)
    - `commission_percent`: Комиссия маркетплейса в процентах (опционально)
    - `discount_percent`: Скидка категории в процентах (опционально)
    - `tax_rate`: Ставка НДС (по умолчанию 0.00)
    """,
    response_description="Созданная политика ценообразования в стандартной обёртке API",
    responses={
        200: {
            "description": "Политика ценообразования успешно создана",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "category_id": 101,
                            "markup_fixed": 100.00,
                            "markup_percent": 15.00,
                            "commission_percent": 5.00,
                            "discount_percent": 2.00,
                            "tax_rate": 20.00,
                        },
                    }
                }
            },
        },
        400: {
            "description": "Некорректные данные (например, значение процента вне диапазона 0-100 или категория не найдена)",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_pricing_policy_invalid_rate_value",
                            "message": "Некорректное значение ставки (должно быть от 0 до 100)",
                            "details": {
                                "field": "markup_percent",
                                "value": "150.00",
                                "reason": "Value must be between 0 and 100",
                            },
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
        409: {
            "description": "Политика уже существует для этой категории",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_pricing_policy_already_exists",
                            "message": "Политика ценообразования для этой категории уже существует",
                        },
                    }
                }
            },
        },
    },
    dependencies=[Depends(require_permissions("category_pricing_policy:create"))],
)
async def create(
    payload: CategoryPricingPolicyCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = CategoryPricingPolicyComposition.build_create_command(db)

    dto = await commands.execute(
        CategoryPricingPolicyCreateDTO(
            category_id=payload.category_id,
            markup_fixed=Decimal(str(payload.markup_fixed)) if payload.markup_fixed is not None else None,
            markup_percent=Decimal(str(payload.markup_percent)) if payload.markup_percent is not None else None,
            commission_percent=Decimal(str(payload.commission_percent)) if payload.commission_percent is not None else None,
            discount_percent=Decimal(str(payload.discount_percent)) if payload.discount_percent is not None else None,
            tax_rate=Decimal(str(payload.tax_rate)),
        ),
        user=user,
    )

    return api_response(
        CategoryPricingPolicyReadSchema.model_validate(dto)
    )


# UPDATE
@category_pricing_policy_commands_router.put(
    "/{pricing_policy_id}",
    summary="Обновить политику ценообразования категории",
    description="""
    Обновляет существующую политику ценообразования.

    Права:
    - Требуется permission: `category_pricing_policy:update`

    Сценарии:
    - Изменение наценок или комиссий категории.
    - Обновление ставки НДС.
    """,
    response_description="Обновлённая политика ценообразования в стандартной обёртке API",
    responses={
        200: {
            "description": "Политика ценообразования успешно обновлена",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "category_id": 101,
                            "markup_fixed": 150.00,
                            "markup_percent": 18.00,
                            "commission_percent": 5.00,
                            "discount_percent": 2.00,
                            "tax_rate": 20.00,
                        },
                    }
                }
            },
        },
        400: {
            "description": "Некорректные данные (например, значение процента вне диапазона 0-100)",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_pricing_policy_invalid_rate_value",
                            "message": "Некорректное значение ставки (должно быть от 0 до 100)",
                            "details": {
                                "field": "tax_rate",
                                "value": "-5.00",
                                "reason": "Tax rate must be between 0 and 100",
                            },
                        },
                    }
                }
            },
        },
        404: {
            "description": "Политика ценообразования не найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_pricing_policy_not_found",
                            "message": "Политика ценообразования категории не найдена",
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("category_pricing_policy:update"))],
)
async def update(
    pricing_policy_id: int,
    payload: CategoryPricingPolicyUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = CategoryPricingPolicyComposition.build_update_command(db)

    dto = await commands.execute(
        pricing_policy_id,
        CategoryPricingPolicyUpdateDTO(
            markup_fixed=Decimal(str(payload.markup_fixed)) if payload.markup_fixed is not None else None,
            markup_percent=Decimal(str(payload.markup_percent)) if payload.markup_percent is not None else None,
            commission_percent=Decimal(str(payload.commission_percent)) if payload.commission_percent is not None else None,
            discount_percent=Decimal(str(payload.discount_percent)) if payload.discount_percent is not None else None,
            tax_rate=Decimal(str(payload.tax_rate)) if payload.tax_rate is not None else None,
        ),
        user=user,
        raw_data=payload.model_dump(exclude_unset=True),
    )

    return api_response(
        CategoryPricingPolicyReadSchema.model_validate(dto)
    )


# DELETE
@category_pricing_policy_commands_router.delete(
    "/{pricing_policy_id}",
    summary="Удалить политику ценообразования категории",
    description="""
    Удаляет политику ценообразования по ID.

    Права:
    - Требуется permission: `category_pricing_policy:delete`

    Сценарии:
    - Удаление неактуальной политики ценообразования.
    - Очистка ошибочно созданной записи.
    """,
    responses={
        200: {
            "description": "Политика ценообразования успешно удалена",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        404: {
            "description": "Политика ценообразования не найдена",
            "content": {
                "application/json": {
                    "example": {
                        "success": False,
                        "error": {
                            "code": "category_pricing_policy_not_found",
                            "message": "Политика ценообразования категории не найдена",
                        },
                    }
                }
            },
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("category_pricing_policy:delete"))],
)
async def delete(
    pricing_policy_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = CategoryPricingPolicyComposition.build_delete_command(db)
    await commands.execute(
        pricing_policy_id,
        user=user,
    )

    return api_response({"deleted": True})
