from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from src.catalog.product.domain.events.base import DomainEvent


@dataclass
class ProductCreatedEvent(DomainEvent):
    """Событие: продукт создан."""
    
    product_id: int
    name: str
    description: Optional[str]
    price: Decimal
    category_id: Optional[int]
    supplier_id: Optional[int]
    product_type_id: Optional[int]
    image_ids: list[int]
    attribute_names: list[str]


@dataclass
class ProductUpdatedEvent(DomainEvent):
    """Событие: продукт обновлён."""
    
    product_id: int
    changed_fields: dict[str, Any]


@dataclass
class ProductDeletedEvent(DomainEvent):
    """Событие: продукт удалён."""
    
    product_id: int


@dataclass
class PriceChangedEvent(DomainEvent):
    """Событие: цена продукта изменена."""
    
    product_id: int
    old_price: Decimal
    new_price: Decimal


@dataclass
class ProductNameChangedEvent(DomainEvent):
    """Событие: имя продукта изменено."""
    
    product_id: int
    old_name: str
    new_name: str


@dataclass
class ProductImageAddedEvent(DomainEvent):
    """Событие: изображение добавлено к продукту."""
    
    product_id: int
    upload_id: int
    is_main: bool
    ordering: int


@dataclass
class ProductImageRemovedEvent(DomainEvent):
    """Событие: изображение удалено из продукта."""
    
    product_id: int
    upload_id: int


@dataclass
class ProductAttributeAddedEvent(DomainEvent):
    """Событие: атрибут добавлен к продукту."""

    product_id: int
    attribute_name: str
    attribute_value: str
    is_filterable: bool
    is_groupable: bool = False


@dataclass
class ProductAttributeRemovedEvent(DomainEvent):
    """Событие: атрибут удалён из продукта."""
    
    product_id: int
    attribute_name: str
