from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductImageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    image_url: str
    is_main: bool


class ProductAttributeSchema(BaseModel):
    name: str
    value: str
    is_filterable: bool = False


class ProductAttributeReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    value: str
    is_filterable: bool


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
