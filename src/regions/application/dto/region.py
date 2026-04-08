from dataclasses import dataclass
from typing import Optional


@dataclass
class RegionReadDTO:
    id: int
    name: str
    parent_id: Optional[int]


@dataclass
class RegionCreateDTO:
    name: str
    parent_id: Optional[int] = None


@dataclass
class RegionUpdateDTO:
    name: Optional[str] = None
    parent_id: Optional[int] = None
