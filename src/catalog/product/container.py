from src.catalog.product.application.commands.create_product import CreateProductCommand
from src.catalog.product.application.commands.delete_product import DeleteProductCommand
from src.catalog.product.application.commands.update_product import UpdateProductCommand
from src.catalog.product.application.queries.product_admin_queries import ProductAdminQueries
from src.catalog.product.application.queries.product_queries import ProductQueries
from src.catalog.product.application.read_models.product_read_repository import ProductReadRepository
from src.catalog.product.domain.repository.audit import ProductAuditRepository
from src.catalog.product.domain.repository.product import ProductRepository
from src.catalog.product.infrastructure.orm.product import SqlAlchemyProductRepository
from src.catalog.product.infrastructure.orm.product_audit import SqlAlchemyProductAuditRepository
from src.core.db.unit_of_work import UnitOfWork
from src.core.di.container import ServiceContainer
from src.core.events import AsyncEventBus, get_event_bus
from src.core.services.images import ImageStorageService, S3ImageStorageService

container = ServiceContainer()

container.register(
    ProductRepository,
    lambda scope, db: SqlAlchemyProductRepository(db),
)

container.register(
    UnitOfWork,
    lambda scope, db: UnitOfWork(db),
)

container.register(
    AsyncEventBus,
    lambda scope, db: get_event_bus(),
)

container.register(
    ImageStorageService,
    lambda scope, db: S3ImageStorageService.from_settings(),
)

container.register(
    ProductReadRepository,
    lambda scope, db: ProductReadRepository(db),
)

container.register(
    ProductQueries,
    lambda scope, db: ProductQueries(
        read_repository=scope.resolve(ProductReadRepository, db=db),
        repository=scope.resolve(ProductRepository, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
    ),
)

container.register(
    CreateProductCommand,
    lambda scope, db: CreateProductCommand(
        repository=scope.resolve(ProductRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateProductCommand,
    lambda scope, db: UpdateProductCommand(
        repository=scope.resolve(ProductRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteProductCommand,
    lambda scope, db: DeleteProductCommand(
        repository=scope.resolve(ProductRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    ProductAuditRepository,
    lambda scope, db: SqlAlchemyProductAuditRepository(db),
)

container.register(
    ProductAdminQueries,
    lambda scope, db: ProductAdminQueries(db),
)
