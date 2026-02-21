from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ProductTypeCreateSchema(BaseModel):
    name: str
    parent_id: Optional[int] = None


class ProductTypeUpdateSchema(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class ProductTypeReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    parent_id: Optional[int]


class ProductTypeListResponse(BaseModel):
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
