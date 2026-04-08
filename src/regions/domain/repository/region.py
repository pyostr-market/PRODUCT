from abc import ABC
from typing import List, Optional

from src.regions.domain.aggregates.region import RegionAggregate


class RegionRepository(ABC):

    async def get(self, region_id: int) -> Optional[RegionAggregate]:
        ...

    async def create(self, aggregate: RegionAggregate) -> RegionAggregate:
        ...

    async def delete(self, region_id: int) -> bool:
        ...

    async def update(self, aggregate: RegionAggregate) -> RegionAggregate:
        ...
