from src.catalog.suppliers.application.commands.create_supplier import (
    CreateSupplierCommand,
)
from src.catalog.suppliers.application.commands.delete_supplier import (
    DeleteSupplierCommand,
)
from src.catalog.suppliers.application.commands.update_supplier import (
    UpdateSupplierCommand,
)
from src.catalog.suppliers.application.queries.supplier_admin_queries import (
    SupplierAdminQueries,
)
from src.catalog.suppliers.application.queries.supplier_queries import SupplierQueries
from src.catalog.suppliers.domain.repository.audit import SupplierAuditRepository
from src.catalog.suppliers.domain.repository.supplier import SupplierRepository
from src.catalog.suppliers.domain.repository.supplier_read import (
    SupplierReadRepositoryInterface,
)
from src.catalog.suppliers.infrastructure.orm.supplier import (
    SqlAlchemySupplierRepository,
)
from src.catalog.suppliers.infrastructure.orm.supplier_audit import (
    SqlAlchemySupplierAuditRepository,
)
from src.catalog.suppliers.infrastructure.orm.supplier_read import (
    SqlAlchemySupplierReadRepository,
)
from src.core.db.unit_of_work import UnitOfWork
from src.core.di.container import ServiceContainer
from src.core.events import AsyncEventBus, get_event_bus

container = ServiceContainer()

container.register(
    SupplierRepository,
    lambda scope, db: SqlAlchemySupplierRepository(db),
)

container.register(
    UnitOfWork,
    lambda scope, db: UnitOfWork(db),
)

container.register(
    AsyncEventBus,
    lambda scope, db: get_event_bus(),
)

# Read Repository - теперь регистрируем интерфейс с инфраструктурной реализацией
container.register(
    SupplierReadRepositoryInterface,
    lambda scope, db: SqlAlchemySupplierReadRepository(db),
)

container.register(
    SupplierQueries,
    lambda scope, db: SupplierQueries(
        read_repository=scope.resolve(SupplierReadRepositoryInterface, db=db)
    ),
)

container.register(
    CreateSupplierCommand,
    lambda scope, db: CreateSupplierCommand(
        repository=scope.resolve(SupplierRepository, db=db),
        audit_repository=scope.resolve(SupplierAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateSupplierCommand,
    lambda scope, db: UpdateSupplierCommand(
        repository=scope.resolve(SupplierRepository, db=db),
        audit_repository=scope.resolve(SupplierAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteSupplierCommand,
    lambda scope, db: DeleteSupplierCommand(
        repository=scope.resolve(SupplierRepository, db=db),
        audit_repository=scope.resolve(SupplierAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    SupplierAuditRepository,
    lambda scope, db: SqlAlchemySupplierAuditRepository(db),
)

container.register(
    SupplierAdminQueries,
    lambda scope, db: SupplierAdminQueries(
        audit_repository=scope.resolve(SupplierAuditRepository, db=db)
    ),
)
