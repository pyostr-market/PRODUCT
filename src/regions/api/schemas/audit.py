from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class RegionAuditReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    region_id: int
    action: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    user_id: int
    fio: Optional[str] = None
    created_at: datetime


class RegionAuditListResponse(BaseModel):
    total: int
    items: List[RegionAuditReadSchema]
