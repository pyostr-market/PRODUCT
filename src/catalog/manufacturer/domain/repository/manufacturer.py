from abc import ABC
from typing import List, Optional

from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)


class ManufacturerRepository(ABC):

    async def get(self, manufacturer_id: int) -> Optional[ManufacturerAggregate]:
        ...

    async def create(self, aggregate: ManufacturerAggregate) -> ManufacturerAggregate:
        ...

    async def delete(self, manufacturer_id: int) -> bool:
        ...

    async def update(self, aggregate: ManufacturerAggregate) -> ManufacturerAggregate:
        ...