from src.catalog.manufacturer.application.dto.audit import ManufacturerAuditDTO
from src.catalog.manufacturer.infrastructure.models.manufacturer_audit_logs import ManufacturerAuditLog


class SqlAlchemyManufacturerAuditRepository:

    def __init__(self, db):
        self.db = db

    async def log(self, dto: ManufacturerAuditDTO):
        model = ManufacturerAuditLog(
            manufacturer_id=dto.manufacturer_id,
            action=dto.action,
            old_data=dto.old_data,
            new_data=dto.new_data,
            user_id=dto.user_id,
        )
        self.db.add(model)
        await self.db.flush()