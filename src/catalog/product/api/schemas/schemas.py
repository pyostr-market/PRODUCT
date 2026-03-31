from decimal import Decimal
from typing import List, Literal, Optional

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class SortTypeEnum(str, Enum):
    """Типы сортировки для каталога товаров."""
    DEFAULT = "default"  # По умолчанию (по ID)
    PRICE_ASC = "price_asc"  # Цена ниже
    PRICE_DESC = "price_desc"  # Цена выше


class FilterOptionSchema(BaseModel):
    """Вариант значения для фильтра."""
    value: str
    count: int = 0  # Опционально: количество товаров с этим значением


class FilterSchema(BaseModel):
    """Отдельный фильтр (атрибут) с вариантами значений."""
    name: str
    is_filterable: bool = True
    options: List[FilterOptionSchema] = Field(default_factory=list)


class CatalogFiltersRequestSchema(BaseModel):
    """Запрос для получения фильтров каталога."""
    category_id: Optional[int] = None
    device_type_id: Optional[int] = None


class CatalogFiltersResponse(BaseModel):
    """Ответ с фильтрами для каталога."""
    filters: List[FilterSchema] = Field(default_factory=list)


class CategoryNestedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None


class SupplierNestedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None


class ProductImageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    upload_id: int  # ID из UploadHistory
    image_url: str  # Публичный URL
    is_main: bool
    ordering: int


class ProductImageReferenceSchema(BaseModel):
    """Ссылка на загруженное изображение для создания товара."""
    model_config = ConfigDict(from_attributes=True)

    upload_id: int  # ID из UploadHistory
    is_main: bool = False
    ordering: int = 0


class ProductImageActionSchema(BaseModel):
    """Операция с изображением при обновлении товара."""
    model_config = ConfigDict(from_attributes=True)

    action: Literal["create", "update", "pass", "delete"]
    upload_id: Optional[int] = None  # ID изображения из UploadHistory
    image_url: Optional[str] = None  # URL изображения (альтернатива upload_id)
    is_main: Optional[bool] = None
    ordering: Optional[int] = None


class ProductAttributeSchema(BaseModel):
    name: str
    value: str
    is_filterable: bool = False


class ProductAttributeReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    value: Optional[str] = ""
    is_filterable: bool


class ProductAttributeCreateSchema(BaseModel):
    name: str
    value: str
    is_filterable: bool = False


class ProductAttributeUpdateSchema(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None
    is_filterable: Optional[bool] = None


class ProductAttributeListResponse(BaseModel):
    total: int
    items: List[ProductAttributeReadSchema]


class ProductCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    images: Optional[List[ProductImageReferenceSchema]] = None
    attributes: List[ProductAttributeSchema] = Field(default_factory=list)


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    images: Optional[List[ProductImageActionSchema]] = None
    attributes: Optional[List[ProductAttributeSchema]] = None


class ProductReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    price: Decimal
    images: List[ProductImageReadSchema]
    attributes: List[ProductAttributeReadSchema]
    category: Optional[CategoryNestedSchema] = None
    supplier: Optional[SupplierNestedSchema] = None


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductReadSchema]


# ==================== ProductRelation ====================

class RelationTypeEnum(str, Enum):
    """Типы связей между товарами."""
    ACCESSORY = "accessory"  # Аксессуары
    SIMILAR = "similar"  # Похожие товары
    BUNDLE = "bundle"  # Комплект
    UPSELL = "upsell"  # Более дорогая альтернатива


class ProductRelationCreateSchema(BaseModel):
    """Схема для создания связи товара."""
    product_id: int
    related_product_id: int
    relation_type: RelationTypeEnum
    sort_order: int = 0


class ProductRelationUpdateSchema(BaseModel):
    """Схема для обновления связи товара."""
    relation_type: Optional[RelationTypeEnum] = None
    sort_order: Optional[int] = None


class ProductRelationReadSchema(BaseModel):
    """Схема для чтения связи товара."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    related_product_id: int
    relation_type: str
    sort_order: int


class ProductRecommendationItemSchema(BaseModel):
    """Схема элемента рекомендации."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: float
    description: Optional[str] = None


class PaginationSchema(BaseModel):
    """Схема пагинации."""
    page: int
    limit: int
    total: int


class ProductRelationListResponse(BaseModel):
    """Ответ со списком связей/рекомендаций."""
    items: List[ProductRecommendationItemSchema]
    pagination: PaginationSchema
