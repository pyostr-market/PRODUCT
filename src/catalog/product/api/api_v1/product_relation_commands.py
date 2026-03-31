from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.schemas import (
    ProductRelationCreateSchema,
    ProductRelationListResponse,
    ProductRelationReadSchema,
    ProductRelationUpdateSchema,
    ProductRecommendationItemSchema,
    PaginationSchema,
    RelationTypeEnum,
)
from src.catalog.product.application.dto.product_relation import (
    ProductRelationCreateDTO,
    ProductRelationUpdateDTO,
)
from src.catalog.product.composition import ProductComposition
from src.core.api.normalizers import normalize_optional_fk
from src.core.api.responses import api_response
from src.core.auth.dependencies import get_current_user, require_permissions
from src.core.auth.schemas.user import User
from src.core.db.database import get_db

product_relation_commands_router = APIRouter(
    tags=["Связи товаров"],
)


@product_relation_commands_router.post(
    "",
    status_code=200,
    summary="Создать связь товара",
    description="""
    Создаёт новую связь между товарами.

    Права:
    - Требуется permission: `product:create`

    Типы связей:
    - `accessory` — аксессуары
    - `similar` — похожие товары
    - `bundle` — комплект
    - `upsell` — более дорогая альтернатива

    Сценарии:
    - Добавление аксессуаров к товару
    - Создание связей между похожими товарами
    - Формирование комплектов

    Ограничения:
    - Связь товара с самим собой не допускается
    - Комбинация product_id + related_product_id + relation_type должна быть уникальной
    """,
    response_description="Созданная связь в стандартной обёртке API",
    responses={
        200: {
            "description": "Связь успешно создана",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "product_id": 5,
                            "related_product_id": 79,
                            "relation_type": "accessory",
                            "sort_order": 1,
                        },
                    }
                }
            },
        },
        400: {
            "description": "Некорректные данные (например, связь с самим собой)",
        },
        404: {
            "description": "Один из товаров не найден",
        },
        409: {
            "description": "Связь уже существует",
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("product:create"))],
)
async def create_product_relation(
    body: ProductRelationCreateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_create_product_relation_command(db)
    dto = await commands.execute(
        ProductRelationCreateDTO(
            product_id=body.product_id,
            related_product_id=body.related_product_id,
            relation_type=body.relation_type.value,
            sort_order=body.sort_order,
        ),
        user=user,
    )

    return api_response(ProductRelationReadSchema.model_validate(dto))


@product_relation_commands_router.put(
    "/{relation_id}",
    summary="Обновить связь товара",
    description="""
    Обновляет связь между товарами по идентификатору.

    Права:
    - Требуется permission: `product:update`

    Сценарии:
    - Изменение типа связи
    - Изменение порядка отображения

    Обновляются только переданные поля.
    """,
    response_description="Обновлённая связь в стандартной обёртке API",
    responses={
        200: {
            "description": "Связь успешно обновлена",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 1,
                            "product_id": 5,
                            "related_product_id": 79,
                            "relation_type": "accessory",
                            "sort_order": 2,
                        },
                    }
                }
            },
        },
        404: {
            "description": "Связь не найдена",
        },
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("product:update"))],
)
async def update_product_relation(
    relation_id: int,
    body: ProductRelationUpdateSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_update_product_relation_command(db)
    dto = await commands.execute(
        relation_id,
        ProductRelationUpdateDTO(
            relation_type=body.relation_type.value if body.relation_type else None,
            sort_order=body.sort_order,
        ),
        user=user,
    )

    return api_response(ProductRelationReadSchema.model_validate(dto))


@product_relation_commands_router.delete(
    "/{relation_id}",
    summary="Удалить связь товара",
    description="""
    Удаляет связь между товарами по идентификатору.

    Права:
    - Требуется permission: `product:delete`

    Сценарии:
    - Удаление неактуальной связи
    - Отзыв аксессуара из продажи
    """,
    response_description="Флаг успешного удаления",
    responses={
        200: {
            "description": "Связь успешно удалена",
            "content": {
                "application/json": {
                    "example": {"success": True, "data": {"deleted": True}}
                }
            },
        },
        404: {"description": "Связь не найдена"},
        403: {"description": "Недостаточно прав"},
    },
    dependencies=[Depends(require_permissions("product:delete"))],
)
async def delete_product_relation(
    relation_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    commands = ProductComposition.build_delete_product_relation_command(db)
    await commands.execute(relation_id, user=user)
    return api_response({"deleted": True})


# ==================== Product Relations Queries ====================

product_relation_q_router = APIRouter(
    tags=["Связи товаров"],
)


@product_relation_q_router.get(
    "/products/{product_id}/relations",
    summary="Получить список связей товара",
    description="""
    Возвращает список связей для товара с пагинацией.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам)

    Query параметры:
    - `relation_type` — опциональный фильтр по типу связи
    - `page` — номер страницы (начиная с 1)
    - `limit` — количество элементов на странице

    Сценарии:
    - Получение списка аксессуаров для товара
    - Получение похожих товаров
    - Отображение комплектов
    """,
    response_description="Список связей с пагинацией",
    responses={
        200: {
            "description": "Список связей успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "items": [
                                {
                                    "id": 79,
                                    "name": "Silicone Case",
                                    "price": 29.99,
                                    "description": "Защитный чехол"
                                }
                            ],
                            "pagination": {
                                "page": 1,
                                "limit": 20,
                                "total": 45
                            }
                        },
                    }
                }
            },
        }
    },
)
async def get_product_relations(
    product_id: int,
    relation_type: Optional[RelationTypeEnum] = Query(None, description="Фильтр по типу связи"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_product_relation_queries(db)
    result = await queries.get_relations(
        product_id=product_id,
        relation_type=relation_type.value if relation_type else None,
        page=page,
        limit=limit,
    )

    return api_response(
        ProductRelationListResponse(
            items=[
                ProductRecommendationItemSchema.model_validate(item)
                for item in result.items
            ],
            pagination=PaginationSchema(
                page=result.page,
                limit=result.limit,
                total=result.total,
            ),
        )
    )


@product_relation_q_router.get(
    "/products/{product_id}/recommendations",
    summary="Получить рекомендации для товара",
    description="""
    Возвращает рекомендации для товара с пагинацией.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам)

    Query параметры:
    - `relation_type` — опциональный фильтр по типу рекомендации
    - `page` — номер страницы (начиная с 1)
    - `limit` — количество элементов на странице

    Сценарии:
    - Блок «Рекомендуемые товары» в карточке товара
    - Блок «Похожие товары»
    - Блок «Аксессуары»
    - Блок «С этим товаром покупают»
    """,
    response_description="Список рекомендаций с пагинацией",
    responses={
        200: {
            "description": "Рекомендации успешно получены",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "items": [
                                {
                                    "id": 79,
                                    "name": "Silicone Case",
                                    "price": 29.99,
                                    "description": "Защитный чехол"
                                },
                                {
                                    "id": 80,
                                    "name": "Screen Protector",
                                    "price": 9.99,
                                    "description": "Защитное стекло"
                                }
                            ],
                            "pagination": {
                                "page": 1,
                                "limit": 20,
                                "total": 12
                            }
                        },
                    }
                }
            },
        }
    },
)
async def get_product_recommendations(
    product_id: int,
    relation_type: Optional[RelationTypeEnum] = Query(None, description="Фильтр по типу рекомендации"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_product_relation_queries(db)
    result = await queries.get_recommendations(
        product_id=product_id,
        relation_type=relation_type.value if relation_type else None,
        page=page,
        limit=limit,
    )

    return api_response(
        ProductRelationListResponse(
            items=[
                ProductRecommendationItemSchema.model_validate(item)
                for item in result.items
            ],
            pagination=PaginationSchema(
                page=result.page,
                limit=result.limit,
                total=result.total,
            ),
        )
    )
