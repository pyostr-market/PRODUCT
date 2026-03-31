from src.catalog.product.domain.repository.product import ProductRepository
from src.catalog.product.domain.repository.product_attribute import ProductAttributeRepository
from src.catalog.product.domain.repository.product_attribute_read import (
    ProductAttributeReadRepositoryInterface,
)
from src.catalog.product.domain.repository.product_audit_query import ProductAuditQueryRepository
from src.catalog.product.domain.repository.product_read import ProductReadRepositoryInterface
from src.catalog.product.domain.repository.product_relation import ProductRelationRepository
from src.catalog.product.domain.repository.product_type import ProductTypeRepository
from src.catalog.product.domain.repository.product_type_audit_query import (
    ProductTypeAuditQueryRepository,
)
from src.catalog.product.domain.repository.product_type_read import ProductTypeReadRepositoryInterface

__all__ = [
    "ProductRepository",
    "ProductAttributeRepository",
    "ProductAttributeReadRepositoryInterface",
    "ProductAuditQueryRepository",
    "ProductReadRepositoryInterface",
    "ProductRelationRepository",
    "ProductTypeRepository",
    "ProductTypeAuditQueryRepository",
    "ProductTypeReadRepositoryInterface",
]
