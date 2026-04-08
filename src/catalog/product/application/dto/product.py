from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING, Literal, Optional

if TYPE_CHECKING:
    from src.catalog.category.domain.aggregates.category import CategoryAggregate
    from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
    from src.regions.domain.aggregates.region import RegionAggregate


@dataclass
class TagReadDTO:
    """DTO для чтения тега."""
    tag_id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


@dataclass
class ProductTagReadDTO:
    """DTO для чтения связи товара с тегом."""
    id: int
    product_id: int
    tag_id: int
    tag: TagReadDTO


@dataclass
class TagCreateDTO:
    """DTO для создания тега."""
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


@dataclass
class TagUpdateDTO:
    """DTO для обновления тега."""
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


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
    is_groupable: bool = False


@dataclass
class ProductAttributeReadDTO:
    name: str
    value: str
    is_filterable: bool
    is_groupable: bool = False
    id: Optional[int] = None


@dataclass
class ProductAttributeCreateDTO:
    name: str
    value: str
    is_filterable: bool = False
    is_groupable: bool = False


@dataclass
class ProductAttributeUpdateDTO:
    name: Optional[str] = None
    value: Optional[str] = None
    is_filterable: Optional[bool] = None
    is_groupable: Optional[bool] = None


@dataclass
class FilterOptionDTO:
    """Вариант значения для фильтра."""
    value: str
    count: int = 0


@dataclass
class FilterDTO:
    """Отдельный фильтр (атрибут) с вариантами значений."""
    name: str
    is_filterable: bool = True
    options: list[FilterOptionDTO] = field(default_factory=list)


@dataclass
class CatalogFiltersDTO:
    """DTO для фильтров каталога."""
    filters: list[FilterDTO] = field(default_factory=list)


@dataclass
class ProductRatingDTO:
    """DTO для рейтинга товара."""
    value: Optional[float] = None
    count: int = 0


@dataclass
class ProductReadDTO:
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    images: list[ProductImageReadDTO] = field(default_factory=list)
    attributes: list[ProductAttributeReadDTO] = field(default_factory=list)
    rating: Optional[ProductRatingDTO] = None
    tags: list[TagReadDTO] = field(default_factory=list)
    category: Optional['CategoryAggregate'] = None
    supplier: Optional['SupplierAggregate'] = None
    region: Optional['RegionAggregate'] = None


@dataclass
class ProductCreateDTO:
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    supplier_id: Optional[int]
    region_id: Optional[int]
    images: list[ProductImageInputDTO]
    attributes: list[ProductAttributeInputDTO]


@dataclass
class ProductUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    region_id: Optional[int] = None
    images: Optional[list[ProductImageOperationDTO]] = None
    attributes: Optional[list[ProductAttributeInputDTO]] = None


@dataclass
class SearchSuggestionDTO:
    """DTO для подсказок следующих слов при поиске."""
    word: str
    count: int


@dataclass
class ProductSearchDTO:
    """DTO для результатов поиска товаров."""
    items: list[ProductReadDTO]
    total: int
    suggestions: list[SearchSuggestionDTO]
