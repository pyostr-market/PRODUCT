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
from src.catalog.suppliers.application.read_models.supplier_read_repository import (
    SupplierReadRepository,
)
from src.catalog.suppliers.domain.repository.audit import SupplierAuditRepository
from src.catalog.suppliers.domain.repository.supplier import SupplierRepository
from src.catalog.suppliers.infrastructure.orm.supplier import (
    SqlAlchemySupplierRepository,
)
from src.catalog.suppliers.infrastructure.orm.supplier_audit import (
    SqlAlchemySupplierAuditRepository,
)
from src.core.db.unit_of_work import UnitOfWork
from src.core.di.container import ServiceContainer

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
    SupplierReadRepository,
    lambda scope, db: SupplierReadRepository(db),
)

container.register(
    SupplierQueries,
    lambda scope, db: SupplierQueries(scope.resolve(SupplierReadRepository, db=db)),
)

container.register(
    CreateSupplierCommand,
    lambda scope, db: CreateSupplierCommand(
        repository=scope.resolve(SupplierRepository, db=db),
        audit_repository=scope.resolve(SupplierAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
    ),
)

container.register(
    UpdateSupplierCommand,
    lambda scope, db: UpdateSupplierCommand(
        repository=scope.resolve(SupplierRepository, db=db),
        audit_repository=scope.resolve(SupplierAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
    ),
)

container.register(
    DeleteSupplierCommand,
    lambda scope, db: DeleteSupplierCommand(
        repository=scope.resolve(SupplierRepository, db=db),
        audit_repository=scope.resolve(SupplierAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
    ),
)

container.register(
    SupplierAuditRepository,
    lambda scope, db: SqlAlchemySupplierAuditRepository(db),
)

container.register(
    SupplierAdminQueries,
    lambda scope, db: SupplierAdminQueries(db),
)
