from src.catalog.product.domain.aggregates.product import ProductAggregate
from src.catalog.product.domain.aggregates.product_relation import (
    ProductRelationAggregate,
    ProductRelationCreatedEvent,
    ProductRelationDeletedEvent,
    ProductRelationUpdatedEvent,
)

__all__ = [
    "ProductAggregate",
    "ProductRelationAggregate",
    "ProductRelationCreatedEvent",
    "ProductRelationDeletedEvent",
    "ProductRelationUpdatedEvent",
]
