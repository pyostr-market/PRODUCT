from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RegionAuditDTO:
    region_id: int
    action: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    user_id: int
    fio: Optional[str] = None
