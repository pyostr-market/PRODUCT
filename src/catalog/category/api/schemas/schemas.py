from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ManufacturerNestedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None


class CategoryNestedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None


class CategoryImageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    upload_id: int  # ID из UploadHistory
    image_url: str  # Публичный URL
    ordering: int


class CategoryImageReferenceSchema(BaseModel):
    """Ссылка на загруженное изображение для создания категории."""
    model_config = ConfigDict(from_attributes=True)

    upload_id: int  # ID из UploadHistory
    ordering: int = 0


class CategoryImageActionSchema(BaseModel):
    """Операция с изображением при обновлении категории."""
    model_config = ConfigDict(from_attributes=True)

    action: Literal["create", "update", "pass", "delete"]
    upload_id: Optional[int] = None  # ID изображения из UploadHistory
    image_url: Optional[str] = None  # URL изображения (альтернатива upload_id)
    ordering: Optional[int] = None


class CategoryCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    images: List[CategoryImageReferenceSchema] = Field(default_factory=list)


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    images: Optional[List[CategoryImageActionSchema]] = None


class CategoryReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    images: List[CategoryImageReadSchema]
    parent: Optional[CategoryNestedSchema] = None
    manufacturer: Optional[ManufacturerNestedSchema] = None


class CategoryListResponse(BaseModel):
    total: int
    items: List[CategoryReadSchema]


# ----------------------------
# Category Pricing Policy Schemas
# ----------------------------

class CategoryPricingPolicyCreateSchema(BaseModel):
    category_id: int
    markup_fixed: Optional[float] = None
    markup_percent: Optional[float] = None
    commission_percent: Optional[float] = None
    discount_percent: Optional[float] = None
    tax_rate: float = 0.00


class CategoryPricingPolicyUpdateSchema(BaseModel):
    markup_fixed: Optional[float] = None
    markup_percent: Optional[float] = None
    commission_percent: Optional[float] = None
    discount_percent: Optional[float] = None
    tax_rate: Optional[float] = None


class CategoryPricingPolicyReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    markup_fixed: Optional[float] = None
    markup_percent: Optional[float] = None
    commission_percent: Optional[float] = None
    discount_percent: Optional[float] = None
    tax_rate: float


class CategoryPricingPolicyListResponse(BaseModel):
    total: int
    items: List[CategoryPricingPolicyReadSchema]
