from abc import ABC

from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO


class SupplierAuditRepository(ABC):

    async def log(self, dto: SupplierAuditDTO):
        ...