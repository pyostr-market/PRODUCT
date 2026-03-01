from abc import ABC
from typing import List, Optional

from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate


class SupplierRepository(ABC):

    async def get(self, supplier_id: int) -> Optional[SupplierAggregate]:
        ...

    async def create(self, aggregate: SupplierAggregate) -> SupplierAggregate:
        ...

    async def delete(self, supplier_id: int) -> bool:
        ...

    async def update(self, aggregate: SupplierAggregate) -> SupplierAggregate:
        ...