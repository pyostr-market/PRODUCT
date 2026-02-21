from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductTypeReadDTO:
    id: int
    name: str
    parent_id: Optional[int] = None


@dataclass
class ProductTypeCreateDTO:
    name: str
    parent_id: Optional[int] = None


@dataclass
class ProductTypeUpdateDTO:
    name: Optional[str] = None
    parent_id: Optional[int] = None
