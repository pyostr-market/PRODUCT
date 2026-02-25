from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.api.schemas.schemas import (
    CategoryPricingPolicyListResponse,
    CategoryPricingPolicyReadSchema,
)
from src.catalog.category.composition import CategoryPricingPolicyComposition
from src.core.api.responses import api_response
from src.core.auth.dependencies import require_permissions
from src.core.db.database import get_db

category_pricing_policy_q_router = APIRouter(
    tags=["Тарификация категории"],
)


# GET BY ID
@category_pricing_policy_q_router.get(
    "/{pricing_policy_id}",
    summary="Получить политику ценообразования по ID",
    description="""
    Возвращает политику ценообразования по её идентификатору.

    Права:
    - Требуется permission: `category_pricing_policy:view`

    Сценарии:
    - Загрузка данных политики ценообразования.
    - Проверка настроек категории.
    """,
    response_description="Политика ценообразования в стандартной обёртке API",
    responses={
        200: {
            "description": "Политика ценообразования найдена",
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
    },
    dependencies=[Depends(require_permissions("category_pricing_policy:view"))],
)
async def get_by_id(
    pricing_policy_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    ### Возможные статусы:

    - **200** — найдена
    - **404** — не найдена
    """

    queries = CategoryPricingPolicyComposition.build_queries(db)
    dto = await queries.get_by_id(pricing_policy_id)

    return api_response(
        CategoryPricingPolicyReadSchema.model_validate(dto)
    )


# GET BY CATEGORY ID
@category_pricing_policy_q_router.get(
    "/by-category/{category_id}",
    summary="Получить политику ценообразования по ID категории",
    description="""
    Возвращает политику ценообразования для указанной категории.

    Права:
    - Требуется permission: `category_pricing_policy:view`

    Сценарии:
    - Получение настроек ценообразования для конкретной категории.
    - Проверка наличия политики ценообразования у категории.
    """,
    response_description="Политика ценообразования в стандартной обёртке API",
    responses={
        200: {
            "description": "Политика ценообразования найдена",
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
    },
    dependencies=[Depends(require_permissions("category_pricing_policy:view"))],
)
async def get_by_category_id(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    ### Возможные статусы:

    - **200** — найдена
    - **404** — не найдена
    """

    queries = CategoryPricingPolicyComposition.build_queries(db)
    dto = await queries.get_by_category_id(category_id)

    return api_response(
        CategoryPricingPolicyReadSchema.model_validate(dto)
    )


# FILTER
@category_pricing_policy_q_router.get(
    "",
    summary="Получить список политик ценообразования",
    description="""
    Возвращает список политик ценообразования с возможностью:

    Права:
    - Требуется permission: `category_pricing_policy:view`

    Сценарии:
    - Построение справочника политик ценообразования в UI.
    - Фильтрация по категории.

    Поддерживается:
    - фильтрации по category_id
    - пагинации (limit, offset)
    """,
    response_description="Список политик ценообразования в стандартной обёртке API",
    responses={
        200: {
            "description": "Список успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 2,
                            "items": [
                                {
                                    "id": 1,
                                    "category_id": 101,
                                    "markup_fixed": 100.00,
                                    "markup_percent": 15.00,
                                    "commission_percent": 5.00,
                                    "discount_percent": 2.00,
                                    "tax_rate": 20.00,
                                },
                                {
                                    "id": 2,
                                    "category_id": 102,
                                    "markup_fixed": 200.00,
                                    "markup_percent": 20.00,
                                    "commission_percent": 7.00,
                                    "discount_percent": 3.00,
                                    "tax_rate": 20.00,
                                },
                            ],
                        },
                    }
                }
            },
        },
    },
    dependencies=[Depends(require_permissions("category_pricing_policy:view"))],
)
async def filter_pricing_policies(
    category_id: int | None = Query(
        None,
        description="Фильтр по ID категории"
    ),
    limit: int = Query(
        10,
        le=100,
        description="Количество записей (макс. 100)"
    ),
    offset: int = Query(
        0,
        description="Смещение"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    ### Возможные статусы:

    - **200** — список успешно получен
    """
    queries = CategoryPricingPolicyComposition.build_queries(db)
    items, total = await queries.filter(category_id, limit, offset)

    return api_response(
        CategoryPricingPolicyListResponse(
            total=total,
            items=[
                CategoryPricingPolicyReadSchema.model_validate(i)
                for i in items
            ],
        )
    )
