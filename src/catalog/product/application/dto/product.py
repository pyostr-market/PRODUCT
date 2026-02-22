from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Optional


@dataclass
class ProductImageReadDTO:
    image_key: str
    image_id: Optional[int] = None
    image_url: Optional[str] = None
    is_main: bool = False
    ordering: int = 0


@dataclass
class ProductImageInputDTO:
    image: bytes
    image_name: str = "test.jpg"
    is_main: bool = False
    ordering: int = 0


@dataclass
class ProductImageOperationDTO:
    """Операция с изображением при обновлении товара."""
    action: Literal["to_create", "to_delete", "pass"]
    image_id: Optional[int] = None  # ID существующего изображения (для to_delete/pass)
    image: Optional[bytes] = None  # Байты нового изображения (для to_create)
    image_name: Optional[str] = None  # Имя файла (для to_create)
    image_url: Optional[str] = None  # URL существующего изображения (альтернатива image_id)
    is_main: bool = False  # Флаг главного изображения
    ordering: Optional[int] = None  # Порядок сортировки (опционально при обновлении)


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
    id: Optional[int] = None


@dataclass
class ProductAttributeCreateDTO:
    name: str
    value: str
    is_filterable: bool = False


@dataclass
class ProductAttributeUpdateDTO:
    name: Optional[str] = None
    value: Optional[str] = None
    is_filterable: Optional[bool] = None


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
    images: Optional[list[ProductImageOperationDTO]] = None
    attributes: Optional[list[ProductAttributeInputDTO]] = None
