from dataclasses import dataclass
from typing import Optional


@dataclass
class SupplierReadDTO:
    id: int
    name: str
    contact_email: Optional[str]
    phone: Optional[str]


@dataclass
class SupplierCreateDTO:
    name: str
    contact_email: Optional[str]
    phone: Optional[str]


@dataclass
class SupplierUpdateDTO:
    name: Optional[str] = None
    contact_email: Optional[str] = None
    phone: Optional[str] = None
