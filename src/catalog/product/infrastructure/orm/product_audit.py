from src.catalog.product.application.dto.audit import ProductAuditDTO
from src.catalog.product.infrastructure.models.product_audit_logs import ProductAuditLog


class SqlAlchemyProductAuditRepository:

    def __init__(self, db):
        self.db = db

    async def log(self, dto: ProductAuditDTO):
        model = ProductAuditLog(
            product_id=dto.product_id,
            action=dto.action,
            old_data=dto.old_data,
            new_data=dto.new_data,
            user_id=dto.user_id,
        )
        self.db.add(model)
        await self.db.flush()
