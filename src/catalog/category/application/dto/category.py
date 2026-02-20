from dataclasses import dataclass
from typing import Optional


@dataclass
class CategoryImageReadDTO:
    ordering: int
    image_key: str
    image_url: Optional[str] = None


@dataclass
class CategoryImageInputDTO:
    image: bytes
    image_name: str = "test.jpg"
    ordering: int = 0


@dataclass
class CategoryReadDTO:
    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    manufacturer_id: Optional[int]
    images: list[CategoryImageReadDTO]


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
