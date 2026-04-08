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
from src.regions.domain.repository.audit import RegionAuditRepository
from src.regions.domain.repository.region import RegionRepository
from src.regions.domain.repository.region_read import (
    RegionReadRepositoryInterface,
)
from src.regions.infrastructure.orm.region import (
    SqlAlchemyRegionRepository,
)
from src.regions.infrastructure.orm.region_audit import (
    SqlAlchemyRegionAuditRepository,
)
from src.regions.infrastructure.orm.region_read import (
    SqlAlchemyRegionReadRepository,
)
from src.core.db.unit_of_work import UnitOfWork
from src.core.di.container import ServiceContainer
from src.core.events import AsyncEventBus, get_event_bus

container = ServiceContainer()

container.register(
    RegionRepository,
    lambda scope, db: SqlAlchemyRegionRepository(db),
)

container.register(
    UnitOfWork,
    lambda scope, db: UnitOfWork(db),
)

container.register(
    AsyncEventBus,
    lambda scope, db: get_event_bus(),
)

# Read Repository - регистрируем интерфейс с инфраструктурной реализацией
container.register(
    RegionReadRepositoryInterface,
    lambda scope, db: SqlAlchemyRegionReadRepository(db),
)

container.register(
    RegionQueries,
    lambda scope, db: RegionQueries(
        read_repository=scope.resolve(RegionReadRepositoryInterface, db=db)
    ),
)

container.register(
    CreateRegionCommand,
    lambda scope, db: CreateRegionCommand(
        repository=scope.resolve(RegionRepository, db=db),
        audit_repository=scope.resolve(RegionAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateRegionCommand,
    lambda scope, db: UpdateRegionCommand(
        repository=scope.resolve(RegionRepository, db=db),
        audit_repository=scope.resolve(RegionAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteRegionCommand,
    lambda scope, db: DeleteRegionCommand(
        repository=scope.resolve(RegionRepository, db=db),
        audit_repository=scope.resolve(RegionAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    RegionAuditRepository,
    lambda scope, db: SqlAlchemyRegionAuditRepository(db),
)

container.register(
    RegionAdminQueries,
    lambda scope, db: RegionAdminQueries(
        audit_repository=scope.resolve(RegionAuditRepository, db=db)
    ),
)
