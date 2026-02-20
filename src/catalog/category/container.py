from src.catalog.category.application.commands.create_category import (
    CreateCategoryCommand,
)
from src.catalog.category.application.commands.delete_category import (
    DeleteCategoryCommand,
)
from src.catalog.category.application.commands.update_category import (
    UpdateCategoryCommand,
)
from src.catalog.category.application.queries.category_admin_queries import (
    CategoryAdminQueries,
)
from src.catalog.category.application.queries.category_queries import CategoryQueries
from src.catalog.category.application.read_models.category_read_repository import (
    CategoryReadRepository,
)
from src.catalog.category.domain.repository.audit import CategoryAuditRepository
from src.catalog.category.domain.repository.category import CategoryRepository
from src.catalog.category.infrastructure.orm.category import (
    SqlAlchemyCategoryRepository,
)
from src.catalog.category.infrastructure.orm.category_audit import (
    SqlAlchemyCategoryAuditRepository,
)
from src.core.db.unit_of_work import UnitOfWork
from src.core.di.container import ServiceContainer
from src.core.events import AsyncEventBus, get_event_bus
from src.core.services.images import ImageStorageService, S3ImageStorageService

container = ServiceContainer()

container.register(
    CategoryRepository,
    lambda scope, db: SqlAlchemyCategoryRepository(db),
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
    CategoryReadRepository,
    lambda scope, db: CategoryReadRepository(db),
)

container.register(
    CategoryQueries,
    lambda scope, db: CategoryQueries(
        read_repository=scope.resolve(CategoryReadRepository, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
    ),
)

container.register(
    CreateCategoryCommand,
    lambda scope, db: CreateCategoryCommand(
        repository=scope.resolve(CategoryRepository, db=db),
        audit_repository=scope.resolve(CategoryAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateCategoryCommand,
    lambda scope, db: UpdateCategoryCommand(
        repository=scope.resolve(CategoryRepository, db=db),
        audit_repository=scope.resolve(CategoryAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteCategoryCommand,
    lambda scope, db: DeleteCategoryCommand(
        repository=scope.resolve(CategoryRepository, db=db),
        audit_repository=scope.resolve(CategoryAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    CategoryAuditRepository,
    lambda scope, db: SqlAlchemyCategoryAuditRepository(db),
)

container.register(
    CategoryAdminQueries,
    lambda scope, db: CategoryAdminQueries(db),
)
