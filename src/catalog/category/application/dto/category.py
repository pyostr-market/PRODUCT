from dataclasses import dataclass
from typing import Optional

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
    upload_id: Optional[int] = None  # ID загруженного изображения из UploadHistory
    image: Optional[bytes] = None  # Байты изображения (для загрузки напрямую)
    image_name: Optional[str] = None  # Имя файла
    ordering: int = 0


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
    images: Optional[list[CategoryImageInputDTO]] = None
