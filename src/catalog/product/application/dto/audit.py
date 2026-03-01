from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ProductAuditDTO:
    product_id: int
    action: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    user_id: int
    fio: Optional[str] = None


@dataclass
class ProductTypeAuditDTO:
    product_type_id: int
    action: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    user_id: int
    fio: Optional[str] = None


@dataclass
class ProductAttributeAuditDTO:
    product_attribute_id: int
    action: str
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    user_id: int
    fio: Optional[str] = None
