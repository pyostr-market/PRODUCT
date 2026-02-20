from src.catalog.manufacturer.domain.repository.manufacturer import (
    ManufacturerRepository,
)
from src.catalog.manufacturer.infrastructure.orm.manufacturer import (
    SqlAlchemyManufacturerRepository,
)
from src.core.di.container import ServiceContainer

from ...core.db.unit_of_work import UnitOfWork
from .application.commands.create_manufacturer import CreateManufacturerCommand
from .application.commands.delete_manufacturer import DeleteManufacturerCommand
from .application.commands.update_manufacturer import UpdateManufacturerCommand
from .application.queries.manufacturer_admin_queries import ManufacturerAdminQueries
from .application.queries.manufacturer_queries import ManufacturerQueries
from .application.read_models.manufacturer_read_repository import (
    ManufacturerReadRepository,
)
from .domain.repository.audit import ManufacturerAuditRepository
from .infrastructure.orm.manufacturer_audit import SqlAlchemyManufacturerAuditRepository

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
    CreateManufacturerCommand,
    lambda scope, db: CreateManufacturerCommand(
        repository=scope.resolve(ManufacturerRepository, db=db),
        audit_repository=scope.resolve(ManufacturerAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
    )
)

container.register(
    UpdateManufacturerCommand,
    lambda scope, db: UpdateManufacturerCommand(
        repository=scope.resolve(ManufacturerRepository, db=db),
        audit_repository=scope.resolve(ManufacturerAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
    )
)

container.register(
    DeleteManufacturerCommand,
    lambda scope, db: DeleteManufacturerCommand(
        repository=scope.resolve(ManufacturerRepository, db=db),
        audit_repository=scope.resolve(ManufacturerAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
    )
)

container.register(
    ManufacturerAuditRepository,
    lambda scope, db: SqlAlchemyManufacturerAuditRepository(db)
)

container.register(
    ManufacturerAdminQueries,
    lambda scope, db: ManufacturerAdminQueries(db)
)