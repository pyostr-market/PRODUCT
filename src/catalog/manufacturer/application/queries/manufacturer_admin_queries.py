from typing import List, Optional, Tuple

from src.catalog.manufacturer.infrastructure.orm.manufacturer_audit_queries import (
    SqlAlchemyManufacturerAuditQueries,
)


class ManufacturerAdminQueries:
    """
    Application layer query сервис для аудита производителей.
    
    Делегирует инфраструктуре работу с ORM, предоставляет
    интерфейс для использования в application layer.
    """

    def __init__(self, audit_queries: SqlAlchemyManufacturerAuditQueries):
        self.audit_queries = audit_queries

    async def filter_logs(
        self,
        manufacturer_id: Optional[int],
        user_id: Optional[int],
        action: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List, int]:
        """
        Фильтрация логов аудита.
        
        Возвращает список записей и общее количество.
        """
        return await self.audit_queries.filter_logs(
            manufacturer_id=manufacturer_id,
            user_id=user_id,
            action=action,
            limit=limit,
            offset=offset,
        )