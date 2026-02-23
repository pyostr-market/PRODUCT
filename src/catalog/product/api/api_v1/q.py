from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.product_type import ProductTypeListResponse, ProductTypeReadSchema
from src.catalog.product.api.schemas.schemas import ProductListResponse, ProductReadSchema
from src.catalog.product.composition import ProductComposition
from src.core.api.responses import api_response
from src.core.db.database import get_db

product_q_router = APIRouter(
    tags=["Товары"],
)


@product_q_router.get(
    "/related/variants",
    summary="Получить связанные товары",
    description="""
    Возвращает список похожих или связанных товаров по `product_id` и/или `name`.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Блок «Похожие товары» в карточке.
    - Поиск альтернатив по названию.
    """,
    response_description="Список связанных товаров в стандартной обёртке API",
    responses={
        200: {
            "description": "Список связанных товаров успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 1,
                            "items": [
                                {
                                    "id": 3002,
                                    "name": "Смартфон X Lite",
                                    "description": "Более доступная версия",
                                    "price": "39990.00",
                                    "category_id": 101,
                                    "supplier_id": 210,
                                    "product_type_id": 5,
                                    "images": [
                                        {
                                            "upload_id": 2,
                                            "image_url": "https://cdn.example.com/product/smartphone-x-lite.jpg",
                                            "is_main": True,
                                            "ordering": 0
                                        }
                                    ],
                                    "attributes": [
                                        {"id": 10, "name": "RAM", "value": "6 GB", "is_filterable": True}
                                    ],
                                    "category": {
                                        "id": 101,
                                        "name": "Смартфоны",
                                        "description": "Мобильные устройства"
                                    },
                                    "supplier": {
                                        "id": 210,
                                        "name": "ООО Поставка Плюс",
                                        "contact_email": "sales@supply-plus.example",
                                        "phone": "+7-999-123-45-67"
                                    },
                                    "product_type": {
                                        "id": 5,
                                        "name": "Смартфоны",
                                        "parent_id": None
                                    }
                                }
                            ],
                        },
                    }
                }
            },
        }
    },
)
async def related_products(
    product_id: int | None = Query(None),
    name: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_queries(db)
    items = await queries.related(product_id=product_id, name=name)

    return api_response(
        ProductListResponse(
            total=len(items),
            items=[ProductReadSchema.model_validate(item) for item in items],
        )
    )


@product_q_router.get(
    "/{product_id}",
    summary="Получить товар по ID",
    description="""
    Возвращает карточку товара по идентификатору.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Открытие страницы товара.
    - Получение товара перед редактированием.
    """,
    response_description="Товар в стандартной обёртке API",
    responses={
        200: {
            "description": "Товар найден",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "id": 3001,
                            "name": "Смартфон X",
                            "description": "Флагманская модель",
                            "price": "59990.00",
                            "category_id": 101,
                            "supplier_id": 210,
                            "product_type_id": 5,
                            "images": [
                                {
                                    "upload_id": 1,
                                    "image_url": "https://cdn.example.com/product/smartphone-x-main.jpg",
                                    "is_main": True,
                                    "ordering": 0
                                }
                            ],
                            "attributes": [
                                {"id": 10, "name": "RAM", "value": "8 GB", "is_filterable": True}
                            ],
                            "category": {
                                "id": 101,
                                "name": "Смартфоны",
                                "description": "Мобильные устройства"
                            },
                            "supplier": {
                                "id": 210,
                                "name": "ООО Поставка Плюс",
                                "contact_email": "sales@supply-plus.example",
                                "phone": "+7-999-123-45-67"
                            },
                            "product_type": {
                                "id": 5,
                                "name": "Смартфоны",
                                "parent_id": None
                            }
                        },
                    }
                }
            },
        },
        404: {"description": "Товар не найден"},
    },
)
async def get_by_id(product_id: int, db: AsyncSession = Depends(get_db)):
    queries = ProductComposition.build_queries(db)
    dto = await queries.get_by_id(product_id)
    return api_response(ProductReadSchema.model_validate(dto))


@product_q_router.get(
    "",
    summary="Получить список товаров",
    description="""
    Возвращает список товаров с фильтрацией и пагинацией.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Каталог товаров на витрине.
    - Выборка товаров по категории или типу.
    - Фильтрация по атрибутам (например, RAM=8GB, Color=Black).

    Поддерживается:
    - фильтрации по имени (частичное совпадение)
    - фильтрации по category_id
    - фильтрации по product_type_id
    - фильтрации по атрибутам (query параметр `attributes` в формате JSON)
    - пагинации (limit, offset)
    """,
    response_description="Список товаров в стандартной обёртке API",
    responses={
        200: {
            "description": "Список товаров успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 2,
                            "items": [
                                {
                                    "id": 3001,
                                    "name": "Смартфон X",
                                    "description": "Флагманская модель",
                                    "price": "59990.00",
                                    "category_id": 101,
                                    "supplier_id": 210,
                                    "product_type_id": 5,
                                    "images": [
                                        {
                                            "upload_id": 1,
                                            "image_url": "https://cdn.example.com/product/smartphone-x.jpg",
                                            "is_main": True,
                                            "ordering": 0
                                        }
                                    ],
                                    "attributes": [
                                        {"id": 10, "name": "RAM", "value": "8 GB", "is_filterable": True}
                                    ],
                                    "category": {
                                        "id": 101,
                                        "name": "Смартфоны",
                                        "description": "Мобильные устройства"
                                    },
                                    "supplier": {
                                        "id": 210,
                                        "name": "ООО Поставка Плюс",
                                        "contact_email": "sales@supply-plus.example",
                                        "phone": "+7-999-123-45-67"
                                    },
                                    "product_type": {
                                        "id": 5,
                                        "name": "Смартфоны",
                                        "parent_id": None
                                    }
                                },
                                {
                                    "id": 3002,
                                    "name": "Смартфон X Lite",
                                    "description": "Более доступная версия",
                                    "price": "39990.00",
                                    "category_id": 101,
                                    "supplier_id": 210,
                                    "product_type_id": 5,
                                    "images": [
                                        {
                                            "upload_id": 2,
                                            "image_url": "https://cdn.example.com/product/smartphone-x-lite.jpg",
                                            "is_main": True,
                                            "ordering": 0
                                        }
                                    ],
                                    "attributes": [
                                        {"id": 10, "name": "RAM", "value": "6 GB", "is_filterable": True}
                                    ],
                                    "category": {
                                        "id": 101,
                                        "name": "Смартфоны",
                                        "description": "Мобильные устройства"
                                    },
                                    "supplier": {
                                        "id": 210,
                                        "name": "ООО Поставка Плюс",
                                        "contact_email": "sales@supply-plus.example",
                                        "phone": "+7-999-123-45-67"
                                    },
                                    "product_type": {
                                        "id": 5,
                                        "name": "Смартфоны",
                                        "parent_id": None
                                    }
                                },
                            ],
                        },
                    }
                }
            },
        }
    },
)
async def filter_products(
    name: str | None = Query(None),
    category_id: int | None = Query(None),
    product_type_id: int | None = Query(None),
    attributes: str | None = Query(
        None,
        description="JSON-объект с атрибутами для фильтрации, например: {\"RAM\": \"8 GB\", \"Color\": \"Black\"}"
    ),
    limit: int = Query(10, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    import json
    
    attributes_dict = None
    if attributes:
        try:
            attributes_dict = json.loads(attributes)
        except json.JSONDecodeError:
            from src.catalog.product.domain.exceptions import ProductInvalidPayload
            raise ProductInvalidPayload(details={"reason": "invalid_attributes_json"})
    
    queries = ProductComposition.build_queries(db)
    items, total = await queries.filter(
        name=name,
        category_id=category_id,
        product_type_id=product_type_id,
        limit=limit,
        offset=offset,
        attributes=attributes_dict,
    )

    return api_response(
        ProductListResponse(
            total=total,
            items=[ProductReadSchema.model_validate(item) for item in items],
        )
    )


# ==================== ProductType ====================

product_type_q_router = APIRouter(
    tags=["Типы продуктов"],
)


@product_type_q_router.get(
    "/type/{product_type_id}",
    summary="Получить тип продукта по ID",
    description="""
    Возвращает тип продукта по его идентификатору.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Загрузка данных типа продукта в фильтре каталога.
    - Проверка корректности привязки товаров к типу.
    """,
    response_description="Данные типа продукта в стандартной обёртке API",
    responses={
        200: {
            "description": "Тип продукта найден",
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
        404: {"description": "Тип продукта не найден"},
    },
)
async def get_product_type_by_id(
    product_type_id: int,
    db: AsyncSession = Depends(get_db)
):
    queries = ProductComposition.build_product_type_queries(db)
    dto = await queries.get_by_id(product_type_id)

    return api_response(
        ProductTypeReadSchema.model_validate(dto)
    )


@product_type_q_router.get(
    "/type",
    summary="Получить список типов продуктов",
    description="""
    Возвращает список типов продуктов с возможностью:

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Построение справочника типов продуктов в UI.
    - Поиск типа продукта по подстроке имени.

    Поддерживается:
    - фильтрации по имени (частичное совпадение)
    - пагинации (limit, offset)
    """,
    response_description="Список типов продуктов в стандартной обёртке API",
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
                                    "id": 5,
                                    "name": "Смартфоны",
                                    "parent_id": None,
                                },
                                {
                                    "id": 6,
                                    "name": "Планшеты",
                                    "parent_id": 5,
                                },
                            ],
                        },
                    }
                }
            },
        },
    },
)
async def filter_product_types(
    name: str | None = Query(
        None,
        description="Фильтр по имени (частичное совпадение)"
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
    queries = ProductComposition.build_product_type_queries(db)
    items, total = await queries.filter(name, limit, offset)

    return api_response(
        ProductTypeListResponse(
            total=total,
            items=[
                ProductTypeReadSchema.model_validate(i)
                for i in items
            ],
        )
    )
