import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EmailTemplateCreateSchema(BaseModel):
    key: str = Field(..., min_length=2, description="Уникальный ключ шаблона")
    subject: str = Field(..., min_length=2, description="Тема письма")
    body_html: str = Field(..., description="HTML тело письма")
    body_text: Optional[str] = Field(default=None, description="Текстовое тело письма")
    variables: Optional[list[str]] = Field(default=None, description="Переменные шаблона")
    is_active: bool = Field(default=True, description="Статус активности")

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError(
                'Ключ должен начинаться с буквы и содержать только буквы, цифры и подчеркивания'
            )
        return v


class EmailTemplateUpdateSchema(BaseModel):
    subject: Optional[str] = Field(default=None, min_length=2, description="Тема письма")
    body_html: Optional[str] = Field(default=None, description="HTML тело письма")
    body_text: Optional[str] = Field(default=None, description="Текстовое тело письма")
    variables: Optional[list[str]] = Field(default=None, description="Переменные шаблона")
    is_active: Optional[bool] = Field(default=None, description="Статус активности")


class EmailTemplateReadSchema(BaseModel):
    id: int
    key: str
    subject: str
    body_html: str
    body_text: Optional[str]
    variables: list[str]
    is_active: bool

    model_config = {'from_attributes': True}


class EmailTemplateListResponse(BaseModel):
    total: int
    items: list[EmailTemplateReadSchema]
