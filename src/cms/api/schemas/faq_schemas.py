from typing import Optional

from pydantic import BaseModel, Field


class FaqCreateSchema(BaseModel):
    question: str = Field(..., min_length=2, description="Вопрос")
    answer: str = Field(..., min_length=2, description="Ответ")
    category: Optional[str] = Field(default=None, min_length=2, description="Категория")
    order: int = Field(default=0, description="Порядок отображения")
    is_active: bool = Field(default=True, description="Статус активности")


class FaqUpdateSchema(BaseModel):
    question: Optional[str] = Field(default=None, min_length=2, description="Вопрос")
    answer: Optional[str] = Field(default=None, min_length=2, description="Ответ")
    category: Optional[str] = Field(default=None, min_length=2, description="Категория")
    order: Optional[int] = Field(default=None, description="Порядок отображения")
    is_active: Optional[bool] = Field(default=None, description="Статус активности")


class FaqReadSchema(BaseModel):
    id: int
    question: str
    answer: str
    category: Optional[str]
    order: int
    is_active: bool

    model_config = {'from_attributes': True}


class FaqListResponse(BaseModel):
    total: int
    items: list[FaqReadSchema]


class FaqCategoryListResponse(BaseModel):
    categories: list[str]
