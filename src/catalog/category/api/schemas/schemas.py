from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.catalog.category.domain.exceptions import CategoryNameTooShort


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

    upload_id: Optional[int] = None  # ID из UploadHistory
    image_url: str  # Публичный URL


class CategoryImageReferenceSchema(BaseModel):
    """Ссылка на загруженное изображение для создания категории."""
    model_config = ConfigDict(from_attributes=True)

    upload_id: int  # ID из UploadHistory


class CategoryImageActionSchema(BaseModel):
    """Операция с изображением при обновлении категории."""
    model_config = ConfigDict(from_attributes=True)

    action: Literal["create", "update", "pass", "delete"]
    upload_id: Optional[int] = None  # ID изображения из UploadHistory
    image_url: Optional[str] = None  # URL изображения (альтернатива upload_id)


class CategoryCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    image: Optional[CategoryImageReferenceSchema] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise CategoryNameTooShort()
        return v.strip()

    @model_validator(mode="after")
    def check_name_length(self):
        if len(self.name) < 2:
            raise CategoryNameTooShort()
        return self


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    image: Optional[CategoryImageActionSchema] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise CategoryNameTooShort()
            return v.strip()
        return v

    @model_validator(mode="after")
    def check_name_length(self):
        if self.name is not None and len(self.name) < 2:
            raise CategoryNameTooShort()
        return self


class CategoryReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    image: Optional[CategoryImageReadSchema] = None
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


class CategoryTreeSchema(BaseModel):
    """Схема категории для иерархического представления (дерево)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    image: Optional[CategoryImageReadSchema] = None
    parent_id: Optional[int] = None
    manufacturer: Optional[ManufacturerNestedSchema] = None
    children: List["CategoryTreeSchema"] = Field(default_factory=list)


CategoryTreeSchema.model_rebuild()


class CategoryTreeResponse(BaseModel):
    """Ответ API для метода дерева категорий."""
    total: int
    items: List[CategoryTreeSchema]
