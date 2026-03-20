from json import loads
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.api.schemas.product_type import (
    ProductTypeListResponse,
    ProductTypeReadSchema,
    ProductTypeTreeResponse,
)
from src.catalog.product.api.schemas.schemas import (
    ProductListResponse,
    ProductReadSchema,
    CatalogFiltersResponse,
    CatalogFiltersRequestSchema,
    FilterSchema,
    FilterOptionSchema,
    SortTypeEnum,
)
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
                                        "parent": None
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
                                "parent": None
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
    - Фильтрация по атрибутам (например, RAM=8GB или RAM=8GB,16GB; Color=Black,White).

    Поддерживается:
    - фильтрации по имени (частичное совпадение)
    - фильтрации по category_id
    - фильтрации по product_type_id
    - фильтрации по списку ID товаров (product_ids)
    - фильтрации по атрибутам (query параметр `attributes` в формате JSON, где значения - массивы)
    - пагинации (limit, offset)

    Пример attributes: {"RAM": ["8 GB", "16 GB"], "Color": ["Black", "White"]}

    Примечание:
    - Если указаны product_ids, возвращаются только товары с указанными ID.
    - Товары, которых не существует, не включаются в результат (без ошибок).
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
                                        "parent": None
                                    }
                                },
                                {
                                    "id": 3002,
                                    "name": "Смартфон X Lite",
                                    "description": "Более доступная версия",
                                    "price": "39990.00",
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
                                        "parent": None
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
    product_ids: List[int] | None = Query(None, description="Список ID товаров для фильтрации"),
    attributes: str | None = Query(
        None,
        description="JSON-объект с атрибутами для фильтрации, например: {\"RAM\": [\"8 GB\", \"16 GB\"], \"Color\": [\"Black\"]}"
    ),
    sort_type: SortTypeEnum = Query(
        SortTypeEnum.DEFAULT,
        description="Тип сортировки: default (по умолчанию), price_asc (цена ниже), price_desc (цена выше)"
    ),
    limit: int = Query(10),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):

    attributes_dict = None
    if attributes:
        try:
            attributes_dict = loads(attributes)
        except Exception:
            from src.catalog.product.domain.exceptions import ProductInvalidPayload
            raise ProductInvalidPayload(details={"reason": "invalid_attributes_json"})

    queries = ProductComposition.build_queries(db)
    items, total = await queries.filter(
        name=name,
        category_id=category_id,
        product_type_id=product_type_id,
        product_ids=product_ids,
        limit=limit,
        offset=offset,
        attributes=attributes_dict,
        sort_type=sort_type.value,
    )

    return api_response(
        ProductListResponse(
            total=total,
            items=[ProductReadSchema.model_validate(item) for item in items],
        )
    )


@product_q_router.get(
    "/catalog/filters",
    summary="Получить фильтры для каталога",
    description="""
    Возвращает список фильтров для каталога товаров.

    Логика работы:
    1. Если указан product_type_id — получаем все filterable атрибуты для этого типа товара
    2. Если указана category_id:
       - Если у категории **есть дочерние категории** — показываем атрибуты товаров всех дочерних категорий
       - Если у категории **нет дочерних категорий** (конечная категория) — показываем атрибуты только товаров этой категории

    Пример:
    - При выборе категории "iPhone 17 Pro Max" (нет дочерних) — вернутся атрибуты только для iPhone 17 Pro Max
    - При выборе категории "iPhone" (есть дочерние: 17, 17 Pro, 17 Pro Max) — вернутся атрибуты для всех iPhone
    - При выборе product_type_id "Смартфоны" — вернутся атрибуты для всех смартфонов (iPhone, Samsung, Xiaomi и т.д.)

    Приоритет параметров:
    - product_type_id имеет наивысший приоритет (если указан, используется он)
    - Если product_type_id не указан, используется category_id

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Построение фильтра в каталоге товаров
    - Получение доступных значений атрибутов для выбранной категории или типа товара

    Поддерживается:
    - фильтрация по product_type_id (прямая фильтрация по типу товара)
    - фильтрация по category_id (с автоматическим определением типа через иерархию)
    - фильтрация по device_type_id (альтернативное имя для product_type_id)
    """,
    response_description="Список фильтров в стандартной обёртке API",
    responses={
        200: {
            "description": "Фильтры успешно получены",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "filters": [
                                {
                                    "name": "RAM",
                                    "is_filterable": True,
                                    "options": [
                                        {"value": "4 GB", "count": 5},
                                        {"value": "8 GB", "count": 10},
                                        {"value": "16 GB", "count": 7}
                                    ]
                                },
                                {
                                    "name": "Color",
                                    "is_filterable": True,
                                    "options": [
                                        {"value": "Black", "count": 12},
                                        {"value": "White", "count": 8},
                                        {"value": "Blue", "count": 6}
                                    ]
                                }
                            ]
                        }
                    }
                }
            },
        }
    },
)
async def get_catalog_filters(
    product_type_id: int | None = Query(None, description="ID типа товара (имеет наивысший приоритет)"),
    category_id: int | None = Query(None, description="ID категории (автоматически определит тип товара через иерархию)"),
    device_type_id: int | None = Query(None, description="Альтернативное имя для product_type_id (для обратной совместимости)"),
    db: AsyncSession = Depends(get_db),
):
    # product_type_id имеет приоритет над device_type_id
    target_type_id = product_type_id if product_type_id is not None else device_type_id
    
    queries = ProductComposition.build_queries(db)
    dto = await queries.get_catalog_filters(
        category_id=category_id,
        device_type_id=target_type_id,
    )

    # Конвертируем DTO в Schema
    filters = [
        FilterSchema(
            name=f.name,
            is_filterable=f.is_filterable,
            options=[
                FilterOptionSchema(value=opt.value, count=opt.count)
                for opt in f.options
            ]
        )
        for f in dto.filters
    ]

    return api_response(
        CatalogFiltersResponse(filters=filters)
    )


# ==================== ProductType ====================

product_type_q_router = APIRouter(
    tags=["Типы продуктов"],
)


@product_type_q_router.get(
    "/type/tree",
    summary="Получить дерево типов продуктов",
    description="""
    Возвращает все типы продуктов в виде иерархического дерева.

    Права:
    - Не требуются (доступно авторизованным и публичным клиентам по политике окружения).

    Сценарии:
    - Построение дерева типов продуктов в UI.
    - Отображение вложенной структуры типов.
    """,
    response_description="Дерево типов продуктов в стандартной обёртке API",
    responses={
        200: {
            "description": "Дерево типов продуктов успешно получено",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "total": 3,
                            "items": [
                                {
                                    "id": 5,
                                    "name": "Смартфоны",
                                    "parent": None,
                                    "children": [
                                        {
                                            "id": 6,
                                            "name": "Планшеты",
                                            "parent": None,
                                            "children": [],
                                            "image": {
                                                "upload_id": 1,
                                                "image_url": "https://cdn.example.com/product-types/tablets.jpg"
                                            }
                                        }
                                    ],
                                    "image": {
                                        "upload_id": 2,
                                        "image_url": "https://cdn.example.com/product-types/smartphones.jpg"
                                    }
                                },
                                {
                                    "id": 7,
                                    "name": "Наушники",
                                    "parent": None,
                                    "children": [],
                                    "image": None
                                },
                            ],
                        },
                    }
                }
            },
        },
    },
)
async def get_product_type_tree(
    db: AsyncSession = Depends(get_db),
):
    queries = ProductComposition.build_product_type_queries(db)
    items, total = await queries.tree()

    return api_response(
        ProductTypeTreeResponse(
            total=total,
            items=[
                ProductTypeReadSchema.model_validate(i)
                for i in items
            ],
        )
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
                            "parent": None,
                            "image": {
                                "upload_id": 1,
                                "image_url": "https://cdn.example.com/product-types/smartphones.jpg"
                            },
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
                                    "parent": None,
                                    "image": {
                                        "upload_id": 1,
                                        "image_url": "https://cdn.example.com/product-types/smartphones.jpg"
                                    }
                                },
                                {
                                    "id": 6,
                                    "name": "Планшеты",
                                    "parent": {
                                        "id": 5,
                                        "name": "Смартфоны"
                                    },
                                    "image": None
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
