from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorSchema(BaseModel):
    code: str
    message: str
    details: dict


class ApiSuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class ApiErrorResponse(BaseModel):
    success: bool = False
    error: ErrorSchema