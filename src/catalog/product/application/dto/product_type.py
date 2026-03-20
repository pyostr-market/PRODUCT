from dataclasses import dataclass, field
from typing import Any, List, Literal, Optional


@dataclass
class ProductTypeImageReadDTO:
    upload_id: int
    image_url: Optional[str] = None


@dataclass
class ProductTypeImageInputDTO:
    upload_id: Optional[int] = None


@dataclass
class ProductTypeImageOperationDTO:
    """Операция с изображением при обновлении типа продукта."""
    action: Literal["create", "update", "delete", "pass"]
    upload_id: Optional[int] = None
    image_url: Optional[str] = None


@dataclass
class ProductTypeReadDTO:
    id: int
    name: str
    parent_id: Optional[int] = None
    parent: Optional[Any] = None
    children: List[Any] = field(default_factory=list)
    image: Optional[ProductTypeImageReadDTO] = None


@dataclass
class ProductTypeCreateDTO:
    name: str
    parent_id: Optional[int] = None
    image: Optional[ProductTypeImageInputDTO] = None


@dataclass
class ProductTypeUpdateDTO:
    name: Optional[str] = None
    parent_id: Optional[int] = None
    image: Optional[ProductTypeImageOperationDTO] = None
