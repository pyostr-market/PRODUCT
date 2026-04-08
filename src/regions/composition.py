from src.regions.application.commands.create_region import (
    CreateRegionCommand,
)
from src.regions.application.commands.delete_region import (
    DeleteRegionCommand,
)
from src.regions.application.commands.update_region import (
    UpdateRegionCommand,
)
from src.regions.application.queries.region_admin_queries import (
    RegionAdminQueries,
)
from src.regions.application.queries.region_queries import RegionQueries
from src.regions.container import container


class RegionComposition:

    @staticmethod
    def build_create_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateRegionCommand, db=db)

    @staticmethod
    def build_update_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateRegionCommand, db=db)

    @staticmethod
    def build_delete_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteRegionCommand, db=db)

    @staticmethod
    def build_queries(db):
        scope = container.create_scope()
        return scope.resolve(RegionQueries, db=db)

    @staticmethod
    def build_admin_queries(db):
        scope = container.create_scope()
        return scope.resolve(RegionAdminQueries, db=db)
