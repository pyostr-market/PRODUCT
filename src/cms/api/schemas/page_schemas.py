import re
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PageBlockNestedSchema(BaseModel):
    """Вложенная схема блока страницы для отображения."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    block_type: str = Field(..., description="Тип блока")
    order: int = Field(0, description="Порядок отображения")
    data: dict[str, Any] = Field(default_factory=dict, description="Данные блока")
    is_active: bool = Field(default=True, description="Статус активности блока")


class PageBlockReadSchema(BaseModel):
    """Схема для чтения блока страницы (legacy API)."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    page_id: int
    block_type: str
    order: int
    data: dict[str, Any]
    is_active: bool


class PageNestedSchema(BaseModel):
    """Вложенная схема страницы для иерархического представления."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str


class PageBlockCreateSchema(BaseModel):
    """Схема для создания блока страницы."""
    model_config = ConfigDict(from_attributes=True)

    block_type: str = Field(..., min_length=1, description="Тип блока (text, image, video, html, etc.)")
    data: dict[str, Any] = Field(default_factory=dict, description="Данные блока")
    order: int = Field(0, ge=0, description="Порядок отображения блока")


class PageBlockActionSchema(BaseModel):
    """Операция с блоком при обновлении страницы."""
    model_config = ConfigDict(from_attributes=True)

    action: str = Field(..., pattern="^(create|update|delete|pass)$", description="Действие над блоком")
    block_id: Optional[int] = Field(None, description="ID существующего блока (для update/delete/pass)")
    block_type: Optional[str] = Field(None, description="Тип блока (требуется для create)")
    data: Optional[dict[str, Any]] = Field(None, description="Данные блока")
    order: Optional[int] = Field(None, ge=0, description="Порядок отображения")


class PageCreateSchema(BaseModel):
    """Схема для создания страницы."""
    model_config = ConfigDict(from_attributes=True)

    slug: str = Field(..., min_length=2, max_length=100, description="URL идентификатор страницы")
    title: str = Field(..., min_length=2, max_length=200, description="Заголовок страницы")
    is_published: bool = Field(default=False, description="Статус публикации")
    blocks: Optional[List[PageBlockCreateSchema]] = Field(default=None, description="Блоки страницы")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug должен содержать только строчные буквы, цифры и дефисы')
        return v


class PageUpdateSchema(BaseModel):
    """Схема для обновления страницы."""
    model_config = ConfigDict(from_attributes=True)

    slug: Optional[str] = Field(default=None, min_length=2, max_length=100, description="URL идентификатор страницы")
    title: Optional[str] = Field(default=None, min_length=2, max_length=200, description="Заголовок страницы")
    is_published: Optional[bool] = Field(default=None, description="Статус публикации")
    blocks: Optional[List[PageBlockActionSchema]] = Field(default=None, description="Операции с блоками")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', v):
            raise ValueError('Slug должен содержать только строчные буквы, цифры и дефисы')
        return v


class PageReadSchema(BaseModel):
    """Схема для чтения страницы."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    is_published: bool
    blocks: List[PageBlockNestedSchema] = Field(default_factory=list)


class PageListResponse(BaseModel):
    """Ответ API для списка страниц."""
    total: int
    items: List[PageReadSchema]


class PageAuditReadSchema(BaseModel):
    """Схема записи аудита страницы."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    page_id: int
    action: str = Field(..., description="Действие (create, update, delete)")
    old_data: Optional[dict[str, Any]] = Field(default=None, description="Старые данные")
    new_data: Optional[dict[str, Any]] = Field(default=None, description="Новые данные")
    user_id: Optional[int] = Field(default=None, description="ID пользователя")
    created_at: str = Field(..., description="Время создания записи")


class PageAuditListResponse(BaseModel):
    """Ответ API для списка записей аудита."""
    total: int
    items: List[PageAuditReadSchema]


class AddBlockSchema(BaseModel):
    """Схема для добавления блока на страницу (legacy API)."""
    model_config = ConfigDict(from_attributes=True)

    block_type: str = Field(..., description="Тип блока")
    data: dict[str, Any] = Field(default_factory=dict, description="Данные блока")
    order: Optional[int] = Field(default=None, description="Порядок отображения")
