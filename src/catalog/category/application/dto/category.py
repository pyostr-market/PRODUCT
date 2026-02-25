from dataclasses import dataclass
from typing import Literal, Optional

from src.catalog.category.domain.aggregates.category import CategoryAggregate
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)


@dataclass
class CategoryImageReadDTO:
    ordering: int
    image_key: str
    image_url: Optional[str] = None
    upload_id: Optional[int] = None


@dataclass
class CategoryImageInputDTO:
    upload_id: int  # ID загруженного изображения из UploadHistory
    ordering: int = 0


@dataclass
class CategoryImageOperationDTO:
    """Операция с изображением при обновлении категории."""
    action: Literal["create", "update", "pass", "delete"]
    upload_id: Optional[int] = None  # ID изображения из UploadHistory
    image_url: Optional[str] = None  # URL изображения (альтернатива upload_id)
    ordering: Optional[int] = None


@dataclass
class CategoryReadDTO:
    id: int
    name: str
    description: Optional[str]
    images: list[CategoryImageReadDTO]
    parent: Optional[CategoryAggregate] = None
    manufacturer: Optional[ManufacturerAggregate] = None


@dataclass
class CategoryCreateDTO:
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    manufacturer_id: Optional[int]
    images: list[CategoryImageInputDTO]


@dataclass
class CategoryUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    images: Optional[list[CategoryImageOperationDTO]] = None
