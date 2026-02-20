from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class ProductImageReadDTO:
    image_key: str
    image_url: Optional[str] = None
    is_main: bool = False


@dataclass
class ProductImageInputDTO:
    image: bytes
    image_name: str = "test.jpg"
    is_main: bool = False


@dataclass
class ProductAttributeInputDTO:
    name: str
    value: str
    is_filterable: bool = False


@dataclass
class ProductAttributeReadDTO:
    name: str
    value: str
    is_filterable: bool


@dataclass
class ProductReadDTO:
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    supplier_id: Optional[int]
    product_type_id: Optional[int]
    images: list[ProductImageReadDTO]
    attributes: list[ProductAttributeReadDTO]


@dataclass
class ProductCreateDTO:
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    supplier_id: Optional[int]
    product_type_id: Optional[int]
    images: list[ProductImageInputDTO]
    attributes: list[ProductAttributeInputDTO]


@dataclass
class ProductUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    product_type_id: Optional[int] = None
    images: Optional[list[ProductImageInputDTO]] = None
    attributes: Optional[list[ProductAttributeInputDTO]] = None
