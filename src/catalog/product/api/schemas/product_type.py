from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict


class ProductTypeImageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    upload_id: int  # ID из UploadHistory
    image_url: str  # Публичный URL


class ProductTypeImageReferenceSchema(BaseModel):
    """Ссылка на загруженное изображение для создания типа продукта."""
    model_config = ConfigDict(from_attributes=True)

    upload_id: int  # ID из UploadHistory


class ProductTypeImageActionSchema(BaseModel):
    """Операция с изображением при обновлении типа продукта."""
    model_config = ConfigDict(from_attributes=True)

    action: Literal["create", "update", "pass", "delete"]
    upload_id: Optional[int] = None  # ID изображения из UploadHistory
    image_url: Optional[str] = None  # URL изображения (альтернатива upload_id)


class ProductTypeNestedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class ProductTypeCreateSchema(BaseModel):
    name: str
    parent_id: Optional[int] = None
    image: Optional[ProductTypeImageReferenceSchema] = None


class ProductTypeUpdateSchema(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    image: Optional[ProductTypeImageActionSchema] = None


class ProductTypeReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    parent_id: Optional[int] = None
    parent: Optional[ProductTypeNestedSchema] = None
    children: List["ProductTypeReadSchema"] = []
    image: Optional[ProductTypeImageReadSchema] = None


ProductTypeReadSchema.model_rebuild()


class ProductTypeListResponse(BaseModel):
    total: int
    items: List[ProductTypeReadSchema]


class ProductTypeTreeResponse(BaseModel):
    total: int
    items: List[ProductTypeReadSchema]


class ProductTypeAuditReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_type_id: int
    action: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    user_id: int
    fio: Optional[str] = None
    created_at: datetime


class ProductTypeAuditListResponse(BaseModel):
    total: int
    items: List[ProductTypeAuditReadSchema]
