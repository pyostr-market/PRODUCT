import json

from src.catalog.product.application.dto.audit import (
    ProductAttributeAuditDTO,
    ProductAuditDTO,
    ProductTypeAuditDTO,
)
from src.catalog.product.domain.repository.audit import ProductRelationAuditDTO
from src.catalog.product.infrastructure.models.product_audit_logs import (
    ProductAttributeAuditLog,
    ProductAuditLog,
    ProductTypeAuditLog,
)
from src.catalog.product.infrastructure.models.product_relation_audit_logs import (
    ProductRelationAuditLog,
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

    async def log_product_relation(self, dto: ProductRelationAuditDTO):
        model = ProductRelationAuditLog(
            relation_id=dto.relation_id,
            action=dto.action,
            old_data=json.dumps(dto.old_data) if dto.old_data else None,
            new_data=json.dumps(dto.new_data) if dto.new_data else None,
            user_id=dto.user_id,
            fio=dto.fio,
        )
        self.db.add(model)
        await self.db.flush()
