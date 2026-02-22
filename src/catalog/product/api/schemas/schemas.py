from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductImageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    image_id: Optional[int] = None
    image_key: str
    image_url: str
    is_main: bool


class ProductImageOperationSchema(BaseModel):
    """Операция с изображением при обновлении товара."""
    model_config = ConfigDict(from_attributes=True)

    action: Literal["to_create", "to_delete", "pass"]
    image_id: Optional[int] = None  # ID существующего изображения (для to_delete/pass)
    image_url: Optional[str] = None  # URL существующего изображения (альтернатива image_id)
    is_main: bool = False  # Флаг главного изображения
    ordering: Optional[int] = None  # Порядок сортировки (опционально)
    
    # Поля только для to_create
    image: Optional[bytes] = None  # Байты изображения
    image_name: Optional[str] = None  # Имя файла


class ProductAttributeSchema(BaseModel):
    name: str
    value: str
    is_filterable: bool = False


class ProductAttributeReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    value: str
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
    product_type_id: Optional[int] = None
    attributes: List[ProductAttributeSchema] = Field(default_factory=list)


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    product_type_id: Optional[int] = None
    images: Optional[List[ProductImageOperationSchema]] = None
    attributes: Optional[List[ProductAttributeSchema]] = None


class ProductReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    supplier_id: Optional[int]
    product_type_id: Optional[int]
    images: List[ProductImageReadSchema]
    attributes: List[ProductAttributeReadSchema]


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductReadSchema]
