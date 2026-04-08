"""DI контейнер для модуля отзывов."""

from redis.asyncio import Redis

from src.catalog.review.application.commands.create_review import CreateReviewCommand
from src.catalog.review.application.commands.delete_review import DeleteReviewCommand
from src.catalog.review.application.commands.update_review import UpdateReviewCommand
from src.catalog.review.application.queries.review_admin_queries import ReviewAdminQueries
from src.catalog.review.application.queries.review_queries import ReviewQueries
from src.catalog.review.domain.repository.review import ReviewRepository
from src.catalog.review.domain.repository.review_audit import (
    ReviewAuditQueryRepository,
    ReviewAuditRepository,
)
from src.catalog.review.infrastructure.orm.review import SqlAlchemyReviewRepository
from src.catalog.review.infrastructure.orm.review_audit import (
    SqlAlchemyReviewAuditQueryRepository,
    SqlAlchemyReviewAuditRepository,
)
from src.core.cache.base import Cache
from src.core.cache.memory import InMemoryCache
from src.core.cache.redis_client import RedisClientFactory
from src.core.db.unit_of_work import UnitOfWork
from src.core.di.container import ServiceContainer
from src.core.events import AsyncEventBus, get_event_bus
from src.core.services.images import ImageStorageService, S3ImageStorageService
from src.uploads.domain.repository.upload_history import UploadHistoryRepository
from src.uploads.infrastructure.orm.upload_history import (
    SqlAlchemyUploadHistoryRepository,
)

container = ServiceContainer()

container.register(
    Redis,
    lambda scope, db: RedisClientFactory.get_client(),
)

container.register(
    Cache,
    lambda scope, db: InMemoryCache(),
)

container.register(
    UploadHistoryRepository,
    lambda scope, db: SqlAlchemyUploadHistoryRepository(db),
)

container.register(
    ReviewRepository,
    lambda scope, db: SqlAlchemyReviewRepository(db),
)

container.register(
    ReviewAuditRepository,
    lambda scope, db: SqlAlchemyReviewAuditRepository(db),
)

container.register(
    ReviewAuditQueryRepository,
    lambda scope, db: SqlAlchemyReviewAuditQueryRepository(db),
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

# Commands
container.register(
    CreateReviewCommand,
    lambda scope, db: CreateReviewCommand(
        repository=scope.resolve(ReviewRepository, db=db),
        audit_repository=scope.resolve(ReviewAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
        upload_history_repository=scope.resolve(UploadHistoryRepository, db=db),
    ),
)

container.register(
    UpdateReviewCommand,
    lambda scope, db: UpdateReviewCommand(
        repository=scope.resolve(ReviewRepository, db=db),
        audit_repository=scope.resolve(ReviewAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
        upload_history_repository=scope.resolve(UploadHistoryRepository, db=db),
    ),
)

container.register(
    DeleteReviewCommand,
    lambda scope, db: DeleteReviewCommand(
        repository=scope.resolve(ReviewRepository, db=db),
        audit_repository=scope.resolve(ReviewAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

# Queries
container.register(
    ReviewQueries,
    lambda scope, db: ReviewQueries(
        repository=scope.resolve(ReviewRepository, db=db),
        image_storage=scope.resolve(ImageStorageService, db=db),
    ),
)

container.register(
    ReviewAdminQueries,
    lambda scope, db: ReviewAdminQueries(
        repository=scope.resolve(ReviewAuditQueryRepository, db=db),
    ),
)
