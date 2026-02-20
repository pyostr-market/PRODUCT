from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SupplierCreateSchema(BaseModel):
    name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None


class SupplierUpdateSchema(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None


class SupplierReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_email: Optional[str]
    phone: Optional[str]


class SupplierListResponse(BaseModel):
    total: int
    items: List[SupplierReadSchema]
