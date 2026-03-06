from src.catalog.product.domain.events.base import DomainEvent
from src.catalog.product.domain.events.product_events import (
    ProductCreatedEvent,
    ProductUpdatedEvent,
    ProductDeletedEvent,
    PriceChangedEvent,
    ProductNameChangedEvent,
    ProductImageAddedEvent,
    ProductImageRemovedEvent,
    ProductAttributeAddedEvent,
    ProductAttributeRemovedEvent,
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
