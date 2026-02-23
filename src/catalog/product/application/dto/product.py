from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Optional

from src.catalog.category.domain.aggregates.category import CategoryAggregate
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate


@dataclass
class ProductImageReadDTO:
    upload_id: int
    image_key: str
    image_url: Optional[str] = None
    is_main: bool = False
    ordering: int = 0


@dataclass
class ProductImageInputDTO:
    upload_id: Optional[int] = None  # ID загруженного изображения из UploadHistory
    image: Optional[bytes] = None  # Байты изображения (для загрузки напрямую)
    image_name: Optional[str] = None  # Имя файла
    is_main: bool = False
    ordering: int = 0


@dataclass
class ProductImageOperationDTO:
    """Операция с изображением при обновлении товара."""
    action: str  # "create", "update", "pass", "delete"
    upload_id: Optional[int] = None  # ID изображения из UploadHistory
    image_url: Optional[str] = None  # URL изображения (альтернатива upload_id)
    is_main: Optional[bool] = None
    ordering: Optional[int] = None


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
    category: Optional[CategoryAggregate] = None
    supplier: Optional[SupplierAggregate] = None
    product_type: Optional[ProductTypeAggregate] = None


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
