"""Pydantic схемы для модуля отзывов."""

from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ==================== Image Schemas ====================

class ReviewImageInputSchema(BaseModel):
    """Ссылка на загруженное изображение для создания отзыва."""
    model_config = ConfigDict(from_attributes=True)

    upload_id: int
    ordering: int = 0


class ReviewImageOperationSchema(BaseModel):
    """Операция с изображением при обновлении отзыва."""
    model_config = ConfigDict(from_attributes=True)

    action: Literal["create", "delete", "pass"]
    upload_id: Optional[int] = None
    ordering: Optional[int] = None


class ReviewImageReadSchema(BaseModel):
    """Схема для чтения изображения отзыва."""
    model_config = ConfigDict(from_attributes=True)

    upload_id: int
    image_url: Optional[str] = None
    ordering: int = 0


# ==================== Review CRUD Schemas ====================

class ReviewCreateSchema(BaseModel):
    """Схема для создания отзыва."""

    product_id: int
    rating: Decimal = Field(..., ge=1, le=5, decimal_places=1)
    text: Optional[str] = Field(None, max_length=5000)
    images: List[ReviewImageInputSchema] = Field(default_factory=list)

    @field_validator('rating', mode='before')
    @classmethod
    def validate_rating(cls, v):
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        return v


class ReviewUpdateSchema(BaseModel):
    """Схема для обновления отзыва."""

    rating: Optional[Decimal] = Field(None, ge=1, le=5, decimal_places=1)
    text: Optional[str] = Field(None, max_length=5000)
    images: Optional[List[ReviewImageOperationSchema]] = None

    @field_validator('rating', mode='before')
    @classmethod
    def validate_rating(cls, v):
        if v is not None and isinstance(v, (int, float)):
            return Decimal(str(v))
        return v


class ReviewReadSchema(BaseModel):
    """Схема для чтения отзыва."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    user_id: int
    username: str
    rating: Decimal
    text: Optional[str] = None
    images: List[ReviewImageReadSchema] = Field(default_factory=list)


class ReviewListResponse(BaseModel):
    """Ответ со списком отзывов."""

    total: int
    items: List[ReviewReadSchema]
    average_rating: Optional[float] = None


# ==================== Audit Schemas ====================

class ReviewAuditReadSchema(BaseModel):
    """Схема для чтения audit лога отзыва."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    review_id: Optional[int] = None
    action: str
    old_data: Optional[dict] = None
    new_data: Optional[dict] = None
    user_id: Optional[int] = None
    fio: Optional[str] = None
    created_at: datetime


class ReviewAuditListResponse(BaseModel):
    """Ответ со списком audit логов."""

    total: int
    items: List[ReviewAuditReadSchema]
