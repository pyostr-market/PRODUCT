from abc import ABC

from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO


class ManufacturerAuditRepository(ABC):

    async def log(self, dto: ManufacturerAuditDTO):
        ...