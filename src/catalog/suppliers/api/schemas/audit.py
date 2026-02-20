from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SupplierAuditReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    supplier_id: int
    action: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    user_id: int
    created_at: datetime


class SupplierAuditListResponse(BaseModel):
    total: int
    items: List[SupplierAuditReadSchema]