from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


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