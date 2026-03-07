from typing import Optional

from pydantic import BaseModel, Field, field_validator

import re


class FeatureFlagCreateSchema(BaseModel):
    key: str = Field(..., min_length=2, description="Уникальный ключ флага")
    enabled: bool = Field(default=False, description="Статус флага")
    description: Optional[str] = Field(default=None, description="Описание флага")

    @field_validator('key')
    @classmethod
    def validate_key(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', v):
            raise ValueError(
                'Ключ должен начинаться с буквы и содержать только буквы, цифры и подчеркивания'
            )
        return v


class FeatureFlagUpdateSchema(BaseModel):
    enabled: Optional[bool] = Field(default=None, description="Статус флага")
    description: Optional[str] = Field(default=None, description="Описание флага")


class FeatureFlagReadSchema(BaseModel):
    id: int
    key: str
    enabled: bool
    description: Optional[str]

    model_config = {'from_attributes': True}


class FeatureFlagListResponse(BaseModel):
    total: int
    items: list[FeatureFlagReadSchema]


class FeatureFlagEnabledListResponse(BaseModel):
    enabled_flags: list[str]
