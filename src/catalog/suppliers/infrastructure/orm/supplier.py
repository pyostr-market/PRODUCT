from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.catalog.suppliers.domain.exceptions import SupplierAlreadyExists, SupplierNotFound
from src.catalog.suppliers.domain.repository.supplier import SupplierRepository
from src.catalog.suppliers.infrastructure.models.supplier import Supplier


class SqlAlchemySupplierRepository(SupplierRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, supplier_id: int) -> Optional[SupplierAggregate]:
        stmt = select(Supplier).where(Supplier.id == supplier_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return SupplierAggregate(
            supplier_id=model.id,
            name=model.name,
            contact_email=model.contact_email,
            phone=model.phone,
        )

    async def get_list(self) -> List[SupplierAggregate]:
        stmt = select(Supplier)
        result = await self.db.execute(stmt)

        return [
            SupplierAggregate(
                supplier_id=m.id,
                name=m.name,
                contact_email=m.contact_email,
                phone=m.phone,
            )
            for m in result.scalars().all()
        ]

    async def create(self, aggregate: SupplierAggregate) -> SupplierAggregate:
        model = Supplier(
            name=aggregate.name,
            contact_email=aggregate.contact_email,
            phone=aggregate.phone,
        )

        self.db.add(model)

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise SupplierAlreadyExists()

        aggregate._set_id(model.id)
        return aggregate

    async def delete(self, supplier_id: int) -> bool:
        model = await self.db.get(Supplier, supplier_id)
        if not model:
            return False

        await self.db.delete(model)
        return True

    async def update(self, aggregate: SupplierAggregate) -> SupplierAggregate:
        model = await self.db.get(Supplier, aggregate.id)

        if not model:
            raise SupplierNotFound()

        model.name = aggregate.name
        model.contact_email = aggregate.contact_email
        model.phone = aggregate.phone

        try:
            await self.db.flush()
        except IntegrityError:
            await self.db.rollback()
            raise SupplierAlreadyExists()

        return aggregate
