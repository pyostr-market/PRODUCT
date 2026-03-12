from dataclasses import dataclass, field
from typing import Any, List, Optional

from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate


@dataclass
class ProductTypeReadDTO:
    id: int
    name: str
    parent_id: Optional[int] = None
    parent: Optional[Any] = None
    children: List[Any] = field(default_factory=list)


@dataclass
class ProductTypeCreateDTO:
    name: str
    parent_id: Optional[int] = None


@dataclass
class ProductTypeUpdateDTO:
    name: Optional[str] = None
    parent_id: Optional[int] = None
