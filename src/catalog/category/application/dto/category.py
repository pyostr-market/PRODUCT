from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Optional

if TYPE_CHECKING:
    from src.catalog.category.domain.aggregates.category import CategoryAggregate
    from src.catalog.manufacturer.domain.aggregates.manufacturer import (
        ManufacturerAggregate,
    )


@dataclass
class CategoryImageReadDTO:
    image_key: str
    image_url: Optional[str] = None
    upload_id: Optional[int] = None


@dataclass
class CategoryImageInputDTO:
    upload_id: int  # ID загруженного изображения из UploadHistory


@dataclass
class CategoryImageOperationDTO:
    """Операция с изображением при обновлении категории."""
    action: Literal["create", "update", "pass", "delete"]
    upload_id: Optional[int] = None  # ID изображения из UploadHistory
    image_url: Optional[str] = None  # URL изображения (альтернатива upload_id)


@dataclass
class CategoryReadDTO:
    id: int
    name: str
    description: Optional[str]
    image: Optional[CategoryImageReadDTO] = None
    parent_id: Optional[int] = None
    parent: Optional['CategoryAggregate'] = None
    manufacturer: Optional['ManufacturerAggregate'] = None
    children: list['CategoryReadDTO'] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


@dataclass
class CategoryCreateDTO:
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    manufacturer_id: Optional[int]
    image: Optional[CategoryImageInputDTO] = None


@dataclass
class CategoryUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    image: Optional[CategoryImageOperationDTO] = None
