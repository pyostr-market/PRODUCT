from src.catalog.manufacturer.infrastructure.orm.manufacturer import (
    SqlAlchemyManufacturerRepository,
)
from src.core.di.container import ServiceContainer

from ...core.db.unit_of_work import UnitOfWork
from .application.commands.manufacturer_commands import ManufacturerCommands
from .application.queries.manufacturer_queries import ManufacturerQueries
from .application.read_models.manufacturer_read_repository import (
    ManufacturerReadRepository,
)
from .domain.repository import ManufacturerRepository

container = ServiceContainer()


# ----------------------------
# Repository registration
# ----------------------------

container.register(
    ManufacturerRepository,
    lambda scope, db: SqlAlchemyManufacturerRepository(db)
)

container.register(
    UnitOfWork,
    lambda scope, db: UnitOfWork(db)
)
# ----------------------------
# CQRS registration
# ----------------------------
container.register(
    ManufacturerReadRepository,
    lambda scope, db: ManufacturerReadRepository(db)
)

container.register(
    ManufacturerQueries,
    lambda scope, db: ManufacturerQueries(
        scope.resolve(ManufacturerReadRepository, db=db)
    )
)


container.register(
    ManufacturerCommands,
    lambda scope, db: ManufacturerCommands(
        repository=scope.resolve(ManufacturerRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
    )
)