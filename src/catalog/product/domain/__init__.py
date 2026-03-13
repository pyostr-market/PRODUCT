from src.catalog.product.domain.events.base import DomainEvent
from src.catalog.product.domain.events.product_events import (
    PriceChangedEvent,
    ProductAttributeAddedEvent,
    ProductAttributeRemovedEvent,
    ProductCreatedEvent,
    ProductDeletedEvent,
    ProductImageAddedEvent,
    ProductImageRemovedEvent,
    ProductNameChangedEvent,
    ProductUpdatedEvent,
)

__all__ = [
    "DomainEvent",
    "ProductCreatedEvent",
    "ProductUpdatedEvent",
    "ProductDeletedEvent",
    "PriceChangedEvent",
    "ProductNameChangedEvent",
    "ProductImageAddedEvent",
    "ProductImageRemovedEvent",
    "ProductAttributeAddedEvent",
    "ProductAttributeRemovedEvent",
]
