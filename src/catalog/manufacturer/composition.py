from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.application.commands.manufacturer_commands import (
    ManufacturerCommands,
)
from src.catalog.manufacturer.application.queries.manufacturer_queries import (
    ManufacturerQueries,
)
from src.catalog.manufacturer.container import container


class ManufacturerComposition:

    @staticmethod
    def build_queries(db: AsyncSession):
        scope = container.create_scope()
        return scope.resolve(ManufacturerQueries, db=db)

    @staticmethod
    def build_commands(db: AsyncSession):
        scope = container.create_scope()
        return scope.resolve(ManufacturerCommands, db=db)