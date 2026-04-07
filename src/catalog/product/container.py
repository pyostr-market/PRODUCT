from redis.asyncio import Redis

from src.catalog.category.domain.repository.category import CategoryRepository
from src.catalog.category.infrastructure.orm.category import (
    SqlAlchemyCategoryRepository,
)
from src.catalog.product.application.commands.create_product import CreateProductCommand
from src.catalog.product.application.commands.create_product_attribute import (
    CreateProductAttributeCommand,
)
from src.catalog.product.application.commands.create_product_relation import (
    CreateProductRelationCommand,
)
from src.catalog.product.application.commands.create_product_type import (
    CreateProductTypeCommand,
)
from src.catalog.product.application.commands.delete_product import DeleteProductCommand
from src.catalog.product.application.commands.delete_product_attribute import (
    DeleteProductAttributeCommand,
)
from src.catalog.product.application.commands.delete_product_relation import (
    DeleteProductRelationCommand,
)
from src.catalog.product.application.commands.delete_product_type import (
    DeleteProductTypeCommand,
)
from src.catalog.product.application.commands.update_product import UpdateProductCommand
from src.catalog.product.application.commands.update_product_attribute import (
    UpdateProductAttributeCommand,
)
from src.catalog.product.application.commands.update_product_relation import (
    UpdateProductRelationCommand,
)
from src.catalog.product.application.commands.update_product_type import (
    UpdateProductTypeCommand,
)
from src.catalog.product.application.queries.product_admin_queries import (
    ProductAdminQueries,
)
from src.catalog.product.application.queries.product_attribute_queries import (
    ProductAttributeQueries,
)
from src.catalog.product.application.queries.product_queries import ProductQueries
from src.catalog.product.application.queries.product_relation_queries import (
    ProductRelationQueries,
)
from src.catalog.product.application.queries.product_type_admin_queries import (
    ProductTypeAdminQueries,
)
from src.catalog.product.application.queries.product_type_queries import (
    ProductTypeQueries,
)
from src.catalog.product.application.queries.tag_queries import TagQueries
from src.catalog.product.application.commands.create_tag import CreateTagCommand
from src.catalog.product.application.commands.update_tag import UpdateTagCommand
from src.catalog.product.application.commands.delete_tag import DeleteTagCommand
from src.catalog.product.application.commands.product_tag_commands import (
    AddProductTagCommand,
    RemoveProductTagCommand,
)
from src.catalog.product.domain.repository.tag import TagRepositoryInterface
from src.catalog.product.domain.repository.product_tag import ProductTagRepositoryInterface
from src.catalog.product.domain.repository.product_tag_read import ProductTagReadRepositoryInterface
from src.catalog.product.infrastructure.orm.tag import SqlAlchemyTagRepository
from src.catalog.product.infrastructure.orm.product_tag import SqlAlchemyProductTagRepository
from src.catalog.product.infrastructure.orm.product_tag_read import SqlAlchemyProductTagReadRepository
from src.catalog.product.application.read_models.product_attribute_read_repository import (
    ProductAttributeReadRepository,
)
from src.catalog.product.application.read_models.product_read_repository import (
    ProductReadRepository,
)
from src.catalog.product.application.read_models.product_type_read_repository import (
    ProductTypeReadRepository,
)
from src.catalog.product.application.services.related_entity_loader import (
    RelatedEntityLoader,
)
from src.catalog.product.domain.repository.audit import ProductAuditRepository
from src.catalog.product.domain.repository.product import ProductRepository
from src.catalog.product.domain.repository.product_attribute import (
    ProductAttributeRepository,
)
from src.catalog.product.domain.repository.product_attribute_read import (
    ProductAttributeReadRepositoryInterface,
)
from src.catalog.product.domain.repository.product_audit_query import (
    ProductAuditQueryRepository,
)
from src.catalog.product.domain.repository.product_read import (
    ProductReadRepositoryInterface,
)
from src.catalog.product.domain.repository.product_relation import ProductRelationRepository
from src.catalog.product.domain.repository.product_type import ProductTypeRepository
from src.catalog.product.domain.repository.product_type_audit_query import (
    ProductTypeAuditQueryRepository,
)
from src.catalog.product.domain.repository.product_type_read import (
    ProductTypeReadRepositoryInterface,
)
from src.catalog.product.infrastructure.orm.cache.cached_product import (
    CachedProductRepository,
)
from src.catalog.product.infrastructure.orm.product import SqlAlchemyProductRepository
from src.catalog.product.infrastructure.orm.product_attribute import (
    SqlAlchemyProductAttributeRepository,
)
from src.catalog.product.infrastructure.orm.product_attribute_read import (
    SqlAlchemyProductAttributeReadRepository,
)
from src.catalog.product.infrastructure.orm.product_audit import (
    SqlAlchemyProductAuditRepository,
)
from src.catalog.product.infrastructure.orm.product_audit_query import (
    SqlAlchemyProductAuditQueryRepository,
)
from src.catalog.product.infrastructure.orm.product_read import (
    SqlAlchemyProductReadRepository,
)
from src.catalog.product.infrastructure.orm.product_relation import (
    SqlAlchemyProductRelationRepository,
)
from src.catalog.product.infrastructure.orm.product_type import (
    SqlAlchemyProductTypeRepository,
)
from src.catalog.product.infrastructure.orm.product_type_audit_query import (
    SqlAlchemyProductTypeAuditQueryRepository,
)
from src.catalog.product.infrastructure.orm.product_type_read import (
    SqlAlchemyProductTypeReadRepository,
)
from src.catalog.suppliers.domain.repository.supplier import SupplierRepository
from src.catalog.suppliers.infrastructure.orm.supplier import (
    SqlAlchemySupplierRepository,
)
from src.core.cache.base import Cache
from src.core.cache.memory import InMemoryCache
from src.core.cache.redis import RedisCache
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

# container.register(
#     ProductRepository,
#     lambda scope, db: SqlAlchemyProductRepository(db),
# )


container.register(
    Redis,
    lambda scope, db: RedisClientFactory.get_client(),
)

container.register(
    Cache,
    lambda scope, db: (
        InMemoryCache()
        # RedisCache(scope.resolve(Redis, db=db))
        # if settings.REDIS_ENABLED
        # else InMemoryCache()
    ),
)

container.register(
    ProductRepository,
    lambda scope, db: CachedProductRepository(
        db_repository=SqlAlchemyProductRepository(db),
        cache=scope.resolve(Cache, db=db),
        ttl=300,
    ),
)
container.register(
    ProductTypeRepository,
    lambda scope, db: SqlAlchemyProductTypeRepository(db),
)

container.register(
    ProductAttributeRepository,
    lambda scope, db: SqlAlchemyProductAttributeRepository(db),
)

container.register(
    ProductRelationRepository,
    lambda scope, db: SqlAlchemyProductRelationRepository(db),
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
    ProductReadRepositoryInterface,
    lambda scope, db: SqlAlchemyProductReadRepository(db),
)

container.register(
    ProductReadRepository,
    lambda scope, db: ProductReadRepository(
        repository=scope.resolve(ProductReadRepositoryInterface, db=db),
    ),
)

container.register(
    ProductTypeReadRepositoryInterface,
    lambda scope, db: SqlAlchemyProductTypeReadRepository(db),
)

container.register(
    ProductTypeReadRepository,
    lambda scope, db: ProductTypeReadRepository(
        repository=scope.resolve(ProductTypeReadRepositoryInterface, db=db),
    ),
)


container.register(
    ProductAttributeReadRepositoryInterface,
    lambda scope, db: SqlAlchemyProductAttributeReadRepository(db),
)

container.register(
    ProductAttributeReadRepository,
    lambda scope, db: ProductAttributeReadRepository(
        repository=scope.resolve(ProductAttributeReadRepositoryInterface, db=db),
    ),
)

# Репозитории для связанных сущностей
container.register(
    CategoryRepository,
    lambda scope, db: SqlAlchemyCategoryRepository(db),
)

container.register(
    SupplierRepository,
    lambda scope, db: SqlAlchemySupplierRepository(db),
)

container.register(
    UploadHistoryRepository,
    lambda scope, db: SqlAlchemyUploadHistoryRepository(db),
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
    ProductTypeQueries,
    lambda scope, db: ProductTypeQueries(
        read_repository=scope.resolve(ProductTypeReadRepository, db=db),
    ),
)

container.register(
    ProductAttributeQueries,
    lambda scope, db: ProductAttributeQueries(
        read_repository=scope.resolve(ProductAttributeReadRepository, db=db),
    ),
)

container.register(
    ProductRelationQueries,
    lambda scope, db: ProductRelationQueries(
        repository=scope.resolve(ProductRelationRepository, db=db),
        db=db,
        image_storage=scope.resolve(ImageStorageService, db=db),
    ),
)

container.register(
    RelatedEntityLoader,
    lambda scope, db: RelatedEntityLoader(
        category_repository=scope.resolve(CategoryRepository, db=db),
        supplier_repository=scope.resolve(SupplierRepository, db=db),
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
        upload_history_repository=scope.resolve(UploadHistoryRepository, db=db),
        entity_loader=scope.resolve(RelatedEntityLoader, db=db),
    ),
)

container.register(
    CreateProductTypeCommand,
    lambda scope, db: CreateProductTypeCommand(
        repository=scope.resolve(ProductTypeRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
        upload_history_repository=scope.resolve(UploadHistoryRepository, db=db),
    ),
)

container.register(
    CreateProductAttributeCommand,
    lambda scope, db: CreateProductAttributeCommand(
        repository=scope.resolve(ProductAttributeRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
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
        upload_history_repository=scope.resolve(UploadHistoryRepository, db=db),
        entity_loader=scope.resolve(RelatedEntityLoader, db=db),
    ),
)

container.register(
    UpdateProductTypeCommand,
    lambda scope, db: UpdateProductTypeCommand(
        repository=scope.resolve(ProductTypeRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
        upload_history_repository=scope.resolve(UploadHistoryRepository, db=db),
    ),
)

container.register(
    UpdateProductAttributeCommand,
    lambda scope, db: UpdateProductAttributeCommand(
        repository=scope.resolve(ProductAttributeRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateProductRelationCommand,
    lambda scope, db: UpdateProductRelationCommand(
        repository=scope.resolve(ProductRelationRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
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
    DeleteProductTypeCommand,
    lambda scope, db: DeleteProductTypeCommand(
        repository=scope.resolve(ProductTypeRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteProductAttributeCommand,
    lambda scope, db: DeleteProductAttributeCommand(
        repository=scope.resolve(ProductAttributeRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    CreateProductRelationCommand,
    lambda scope, db: CreateProductRelationCommand(
        repository=scope.resolve(ProductRelationRepository, db=db),
        product_repository=scope.resolve(ProductRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteProductRelationCommand,
    lambda scope, db: DeleteProductRelationCommand(
        repository=scope.resolve(ProductRelationRepository, db=db),
        audit_repository=scope.resolve(ProductAuditRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    ProductAuditRepository,
    lambda scope, db: SqlAlchemyProductAuditRepository(db),
)

container.register(
    ProductAuditQueryRepository,
    lambda scope, db: SqlAlchemyProductAuditQueryRepository(db),
)

container.register(
    ProductAdminQueries,
    lambda scope, db: ProductAdminQueries(
        repository=scope.resolve(ProductAuditQueryRepository, db=db),
    ),
)

container.register(
    ProductTypeAuditQueryRepository,
    lambda scope, db: SqlAlchemyProductTypeAuditQueryRepository(db),
)

container.register(
    ProductTypeAdminQueries,
    lambda scope, db: ProductTypeAdminQueries(
        repository=scope.resolve(ProductTypeAuditQueryRepository, db=db),
    ),
)

# ==================== Tags ====================

container.register(
    TagRepositoryInterface,
    lambda scope, db: SqlAlchemyTagRepository(db),
)

container.register(
    ProductTagRepositoryInterface,
    lambda scope, db: SqlAlchemyProductTagRepository(db),
)

container.register(
    ProductTagReadRepositoryInterface,
    lambda scope, db: SqlAlchemyProductTagReadRepository(db),
)

container.register(
    TagQueries,
    lambda scope, db: TagQueries(
        tag_repository=scope.resolve(TagRepositoryInterface, db=db),
        product_tag_read_repository=scope.resolve(ProductTagReadRepositoryInterface, db=db),
    ),
)

container.register(
    CreateTagCommand,
    lambda scope, db: CreateTagCommand(
        repository=scope.resolve(TagRepositoryInterface, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateTagCommand,
    lambda scope, db: UpdateTagCommand(
        repository=scope.resolve(TagRepositoryInterface, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteTagCommand,
    lambda scope, db: DeleteTagCommand(
        repository=scope.resolve(TagRepositoryInterface, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    AddProductTagCommand,
    lambda scope, db: AddProductTagCommand(
        product_tag_repository=scope.resolve(ProductTagRepositoryInterface, db=db),
        product_repository=scope.resolve(ProductRepository, db=db),
        tag_repository=scope.resolve(TagRepositoryInterface, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    RemoveProductTagCommand,
    lambda scope, db: RemoveProductTagCommand(
        product_tag_repository=scope.resolve(ProductTagRepositoryInterface, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)
