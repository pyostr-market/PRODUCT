from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductRelationCreateDTO:
    """DTO для создания связи товара."""
    product_id: int
    related_product_id: int
    relation_type: str
    sort_order: int = 0


@dataclass
class ProductRelationUpdateDTO:
    """DTO для обновления связи товара."""
    relation_type: Optional[str] = None
    sort_order: Optional[int] = None


@dataclass
class ProductRelationReadDTO:
    """DTO для чтения связи товара."""
    id: int
    product_id: int
    related_product_id: int
    relation_type: str
    sort_order: int


@dataclass
class ProductRelationListItemDTO:
    """DTO для элемента списка рекомендаций."""
    id: int
    name: str
    price: float
    description: Optional[str] = None
