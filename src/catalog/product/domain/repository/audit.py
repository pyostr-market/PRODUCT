from abc import ABC

from src.catalog.product.application.dto.audit import ProductAuditDTO


class ProductAuditRepository(ABC):

    async def log(self, dto: ProductAuditDTO):
        ...
