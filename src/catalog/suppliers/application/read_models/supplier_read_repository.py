from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.suppliers.application.dto.supplier import SupplierReadDTO
from src.catalog.suppliers.infrastructure.models.supplier import Supplier


class SupplierReadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, supplier_id: int) -> Optional[SupplierReadDTO]:
        stmt = select(
            Supplier.id,
            Supplier.name,
            Supplier.contact_email,
            Supplier.phone,
        ).where(Supplier.id == supplier_id)

        result = await self.db.execute(stmt)
        row = result.first()

        if not row:
            return None

        return SupplierReadDTO(*row)

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[SupplierReadDTO], int]:

        stmt = select(
            Supplier.id,
            Supplier.name,
            Supplier.contact_email,
            Supplier.phone,
        )

        count_stmt = select(func.count()).select_from(Supplier)

        if name:
            stmt = stmt.where(Supplier.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(Supplier.name.ilike(f"%{name}%"))

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [SupplierReadDTO(*row) for row in result.all()]
        total = count_result.scalar() or 0
        return items, total
