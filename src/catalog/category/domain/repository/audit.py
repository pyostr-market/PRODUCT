from abc import ABC

from src.catalog.category.application.dto.audit import CategoryAuditDTO


class CategoryAuditRepository(ABC):

    async def log(self, dto: CategoryAuditDTO):
        ...
