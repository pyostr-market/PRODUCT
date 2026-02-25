from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class CategoryPricingPolicyAuditDTO:
    pricing_policy_id: int
    action: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    user_id: int
    fio: Optional[str] = None
