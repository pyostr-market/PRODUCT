from typing import Optional

from src.catalog.manufacturer.application.read_models.manufacturer_read_repository import (
    ManufacturerReadRepository,
)
from src.catalog.manufacturer.domain.exceptions import ManufacturerNotFound


class ManufacturerQueries:

    def __init__(self, read_repository: ManufacturerReadRepository):
        self.read_repository = read_repository

    async def get_by_id(self, manufacturer_id: int):
        result = await self.read_repository.get_by_id(manufacturer_id)
        if not result:
            raise ManufacturerNotFound()
        return result

    async def filter(self, name: Optional[str], limit: int, offset: int):
        return await self.read_repository.filter(name, limit, offset)