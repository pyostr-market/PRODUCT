from src.catalog.category.application.dto.audit import CategoryAuditDTO
from src.catalog.category.infrastructure.models.category_audit_logs import (
    CategoryAuditLog,
)


class SqlAlchemyCategoryAuditRepository:

    def __init__(self, db):
        self.db = db

    async def log(self, dto: CategoryAuditDTO):
        model = CategoryAuditLog(
            category_id=dto.category_id,
            action=dto.action,
            old_data=dto.old_data,
            new_data=dto.new_data,
            user_id=dto.user_id,
            fio=dto.fio,
        )
        self.db.add(model)
        await self.db.flush()
