from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.manufacturer.application.commands.create_manufacturer import CreateManufacturerCommand
from src.catalog.manufacturer.application.commands.update_manufacturer import UpdateManufacturerCommand
from src.catalog.manufacturer.application.commands.delete_manufacturer import DeleteManufacturerCommand
from src.catalog.manufacturer.application.queries.manufacturer_admin_queries import ManufacturerAdminQueries
from src.catalog.manufacturer.application.queries.manufacturer_queries import (
    ManufacturerQueries,
)
from src.catalog.manufacturer.container import container

class ManufacturerComposition:

    @staticmethod
    def build_create_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateManufacturerCommand, db=db)

    @staticmethod
    def build_update_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateManufacturerCommand, db=db)

    @staticmethod
    def build_delete_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteManufacturerCommand, db=db)

    @staticmethod
    def build_queries(db):
        scope = container.create_scope()
        return scope.resolve(ManufacturerQueries, db=db)

    @staticmethod
    def build_admin_queries(db):
        scope = container.create_scope()
        return scope.resolve(ManufacturerAdminQueries, db=db)