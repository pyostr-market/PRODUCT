from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

import re


class PageBlockCreateSchema(BaseModel):
    block_type: str = Field(..., description="Тип блока")
    data: dict[str, Any] = Field(default_factory=dict, description="Данные блока")
    order: int = Field(default=0, description="Порядок отображения")


class PageCreateSchema(BaseModel):
    slug: str = Field(..., min_length=2, description="URL идентификатор страницы")
    title: str = Field(..., min_length=2, description="Заголовок страницы")
    is_published: bool = Field(default=False, description="Статус публикации")
    blocks: Optional[list[PageBlockCreateSchema]] = Field(default=None, description="Блоки страницы")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug должен содержать только строчные буквы, цифры и дефисы')
        return v


class PageUpdateSchema(BaseModel):
    slug: Optional[str] = Field(default=None, min_length=2, description="URL идентификатор страницы")
    title: Optional[str] = Field(default=None, min_length=2, description="Заголовок страницы")
    is_published: Optional[bool] = Field(default=None, description="Статус публикации")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug должен содержать только строчные буквы, цифры и дефисы')
        return v


class PageBlockReadSchema(BaseModel):
    id: Optional[int]
    page_id: int
    block_type: str
    order: int
    data: dict[str, Any]
    is_active: bool

    model_config = {'from_attributes': True}


class PageReadSchema(BaseModel):
    id: int
    slug: str
    title: str
    is_published: bool
    blocks: list[PageBlockReadSchema]

    model_config = {'from_attributes': True}


class PageListResponse(BaseModel):
    total: int
    items: list[PageReadSchema]


class AddBlockSchema(BaseModel):
    block_type: str = Field(..., description="Тип блока")
    data: dict[str, Any] = Field(default_factory=dict, description="Данные блока")
    order: Optional[int] = Field(default=None, description="Порядок отображения")
