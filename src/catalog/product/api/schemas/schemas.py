from decimal import Decimal
from typing import List, Literal, Optional

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field


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


class ProductTypeNestedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    parent: Optional["ProductTypeNestedSchema"] = None


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
    product_type_id: Optional[int] = None
    attributes: List[ProductAttributeSchema] = Field(default_factory=list)


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    product_type_id: Optional[int] = None
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
    product_type: Optional[ProductTypeNestedSchema] = None


class ProductListResponse(BaseModel):
    total: int
    items: List[ProductReadSchema]
