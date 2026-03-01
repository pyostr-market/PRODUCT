from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductAttributeReadDTO:
    id: int
    name: str
    value: str = ""
    is_filterable: bool = False
