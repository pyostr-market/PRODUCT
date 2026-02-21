from src.catalog.product.application.dto.audit import ProductAuditDTO, ProductAttributeAuditDTO, ProductTypeAuditDTO
from src.catalog.product.infrastructure.models.product_audit_logs import (
    ProductAuditLog,
    ProductAttributeAuditLog,
    ProductTypeAuditLog,
)


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
            fio=dto.fio,
        )
        self.db.add(model)
        await self.db.flush()

    async def log_product_type(self, dto: ProductTypeAuditDTO):
        model = ProductTypeAuditLog(
            product_type_id=dto.product_type_id,
            action=dto.action,
            old_data=dto.old_data,
            new_data=dto.new_data,
            user_id=dto.user_id,
            fio=dto.fio,
        )
        self.db.add(model)
        await self.db.flush()

    async def log_product_attribute(self, dto: ProductAttributeAuditDTO):
        model = ProductAttributeAuditLog(
            product_attribute_id=dto.product_attribute_id,
            action=dto.action,
            old_data=dto.old_data,
            new_data=dto.new_data,
            user_id=dto.user_id,
            fio=dto.fio,
        )
        self.db.add(model)
        await self.db.flush()
