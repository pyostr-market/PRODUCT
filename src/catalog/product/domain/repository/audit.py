from abc import ABC

from src.catalog.product.application.dto.audit import (
    ProductAttributeAuditDTO,
    ProductAuditDTO,
    ProductTypeAuditDTO,
)


class ProductAuditRepository(ABC):

    async def log(self, dto: ProductAuditDTO):
        ...

    async def log_product_type(self, dto: ProductTypeAuditDTO):
        ...

    async def log_product_attribute(self, dto: ProductAttributeAuditDTO):
        ...
