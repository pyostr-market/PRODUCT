from typing import List, Optional

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


class CategoryImageSchema(BaseModel):
    upload_id: int  # ID загруженного изображения из UploadHistory
    ordering: int = 0


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
    images: Optional[List[CategoryImageReferenceSchema]] = None


class CategoryReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    manufacturer_id: Optional[int]
    images: List[CategoryImageReadSchema]
    parent: Optional[CategoryNestedSchema] = None
    manufacturer: Optional[ManufacturerNestedSchema] = None


class CategoryListResponse(BaseModel):
    total: int
    items: List[CategoryReadSchema]
