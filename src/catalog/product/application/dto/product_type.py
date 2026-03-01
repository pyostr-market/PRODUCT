from dataclasses import dataclass
from typing import Optional

from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate


@dataclass
class ProductTypeReadDTO:
    id: int
    name: str
    parent: Optional[ProductTypeAggregate] = None


@dataclass
class ProductTypeCreateDTO:
    name: str
    parent_id: Optional[int] = None


@dataclass
class ProductTypeUpdateDTO:
    name: Optional[str] = None
    parent_id: Optional[int] = None
