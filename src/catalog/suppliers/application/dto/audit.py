from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SupplierAuditDTO:
    supplier_id: int
    action: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    user_id: int