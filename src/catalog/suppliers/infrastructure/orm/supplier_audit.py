from src.catalog.suppliers.application.dto.audit import SupplierAuditDTO
from src.catalog.suppliers.infrastructure.models.supplier_audit_logs import (
    SupplierAuditLog,
)


class SqlAlchemySupplierAuditRepository:

    def __init__(self, db):
        self.db = db

    async def log(self, dto: SupplierAuditDTO):
        model = SupplierAuditLog(
            supplier_id=dto.supplier_id,
            action=dto.action,
            old_data=dto.old_data,
            new_data=dto.new_data,
            user_id=dto.user_id,
            fio=dto.fio,
        )
        self.db.add(model)
        await self.db.flush()