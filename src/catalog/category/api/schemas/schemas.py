from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryImageSchema(BaseModel):
    image: bytes = Field(default=b"test.jpg", examples=["dGVzdC5qcGc="])
    image_name: str = "test.jpg"
    ordering: int = 0


class CategoryImageReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ordering: int
    image_url: str


class CategoryCreateSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Электроника",
                "description": "Категория электроники",
                "images": [
                    {
                        "image": "dGVzdC5qcGc=",
                        "image_name": "test.jpg",
                        "ordering": 0,
                    }
                ],
            }
        }
    )

    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    images: List[CategoryImageSchema] = Field(default_factory=lambda: [CategoryImageSchema()])


class CategoryUpdateSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Обновленная категория",
                "images": [
                    {
                        "image": "dGVzdC5qcGc=",
                        "image_name": "test.jpg",
                        "ordering": 0,
                    }
                ],
            }
        }
    )

    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    images: Optional[List[CategoryImageSchema]] = None


class CategoryReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    manufacturer_id: Optional[int]
    images: List[CategoryImageReadSchema]


class CategoryListResponse(BaseModel):
    total: int
    items: List[CategoryReadSchema]
