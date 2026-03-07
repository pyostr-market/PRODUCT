from typing import Optional

from pydantic import BaseModel, Field


class SeoCreateSchema(BaseModel):
    page_slug: str = Field(..., min_length=2, description="Slug страницы")
    title: Optional[str] = Field(default=None, description="SEO заголовок")
    description: Optional[str] = Field(default=None, description="SEO описание")
    keywords: Optional[list[str]] = Field(default=None, description="Ключевые слова")
    og_image_id: Optional[int] = Field(default=None, description="ID изображения для OG")


class SeoUpdateSchema(BaseModel):
    title: Optional[str] = Field(default=None, description="SEO заголовок")
    description: Optional[str] = Field(default=None, description="SEO описание")
    keywords: Optional[list[str]] = Field(default=None, description="Ключевые слова")
    og_image_id: Optional[int] = Field(default=None, description="ID изображения для OG")


class SeoReadSchema(BaseModel):
    id: int
    page_slug: str
    title: Optional[str]
    description: Optional[str]
    keywords: list[str]
    og_image_id: Optional[int]

    model_config = {'from_attributes': True}


class SeoMetaResponse(BaseModel):
    """Ответ с meta тегами для фронтенда."""
    title: Optional[str]
    description: Optional[str]
    keywords: Optional[str]
    og_image_id: Optional[int]
