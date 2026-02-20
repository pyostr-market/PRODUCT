from dataclasses import dataclass
from typing import Optional


@dataclass
class ManufacturerReadDTO:
    id: int
    name: str
    description: Optional[str]


@dataclass
class ManufacturerCreateDTO:
    name: str
    description: Optional[str]


@dataclass
class ManufacturerUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None