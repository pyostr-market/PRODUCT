from src.cms.application.commands.add_page_block import AddPageBlockCommand
from src.cms.application.commands.create_email_template import (
    CreateEmailTemplateCommand,
)
from src.cms.application.commands.create_faq import CreateFaqCommand
from src.cms.application.commands.create_feature_flag import CreateFeatureFlagCommand
from src.cms.application.commands.create_page import CreatePageCommand
from src.cms.application.commands.create_seo import CreateSeoCommand
from src.cms.application.commands.delete_email_template import (
    DeleteEmailTemplateCommand,
)
from src.cms.application.commands.delete_faq import DeleteFaqCommand
from src.cms.application.commands.delete_feature_flag import DeleteFeatureFlagCommand
from src.cms.application.commands.delete_page import DeletePageCommand
from src.cms.application.commands.delete_seo import DeleteSeoCommand
from src.cms.application.commands.update_email_template import (
    UpdateEmailTemplateCommand,
)
from src.cms.application.commands.update_faq import UpdateFaqCommand
from src.cms.application.commands.update_feature_flag import UpdateFeatureFlagCommand
from src.cms.application.commands.update_page import UpdatePageCommand
from src.cms.application.commands.update_seo import UpdateSeoCommand
from src.cms.application.queries.email_template_queries import EmailTemplateQueries
from src.cms.application.queries.faq_queries import FaqQueries
from src.cms.application.queries.feature_flag_queries import FeatureFlagQueries
from src.cms.application.queries.page_queries import PageQueries
from src.cms.application.queries.seo_queries import SeoQueries
from src.cms.domain.repository.email_template import EmailTemplateRepository
from src.cms.domain.repository.faq import FaqRepository
from src.cms.domain.repository.feature_flag import FeatureFlagRepository
from src.cms.domain.repository.page import PageRepository
from src.cms.domain.repository.seo import SeoRepository
from src.cms.domain.services.page_slug_uniqueness_service import (
    PageSlugUniquenessService,
)
from src.cms.infrastructure.orm.email_template import SqlAlchemyEmailTemplateRepository
from src.cms.infrastructure.orm.faq import SqlAlchemyFaqRepository
from src.cms.infrastructure.orm.feature_flag import SqlAlchemyFeatureFlagRepository
from src.cms.infrastructure.orm.page import SqlAlchemyPageRepository
from src.cms.infrastructure.orm.seo import SqlAlchemySeoRepository
from src.cms.infrastructure.services.page_slug_uniqueness_service import (
    PageSlugUniquenessServiceImpl,
)
from src.core.db.unit_of_work import UnitOfWork
from src.core.di.container import ServiceContainer
from src.core.events import AsyncEventBus, get_event_bus

container = ServiceContainer()

# ==================== Unit of Work ====================

container.register(
    UnitOfWork,
    lambda scope, db: UnitOfWork(db),
)

# ==================== Event Bus ====================

container.register(
    AsyncEventBus,
    lambda scope, db: get_event_bus(),
)

# ==================== Repositories ====================

container.register(
    PageRepository,
    lambda scope, db: SqlAlchemyPageRepository(db),
)

container.register(
    FaqRepository,
    lambda scope, db: SqlAlchemyFaqRepository(db),
)

container.register(
    EmailTemplateRepository,
    lambda scope, db: SqlAlchemyEmailTemplateRepository(db),
)

container.register(
    FeatureFlagRepository,
    lambda scope, db: SqlAlchemyFeatureFlagRepository(db),
)

container.register(
    SeoRepository,
    lambda scope, db: SqlAlchemySeoRepository(db),
)

# ==================== Domain Services ====================

container.register(
    PageSlugUniquenessService,
    lambda scope, db: PageSlugUniquenessServiceImpl(
        page_repository=scope.resolve(PageRepository, db=db),
    ),
)

# ==================== Queries ====================

container.register(
    PageQueries,
    lambda scope, db: PageQueries(db),
)

container.register(
    FaqQueries,
    lambda scope, db: FaqQueries(db),
)

container.register(
    EmailTemplateQueries,
    lambda scope, db: EmailTemplateQueries(db),
)

container.register(
    FeatureFlagQueries,
    lambda scope, db: FeatureFlagQueries(db),
)

container.register(
    SeoQueries,
    lambda scope, db: SeoQueries(db),
)

# ==================== Commands: Pages ====================

container.register(
    CreatePageCommand,
    lambda scope, db: CreatePageCommand(
        repository=scope.resolve(PageRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
        slug_uniqueness_service=scope.resolve(PageSlugUniquenessService, db=db),
    ),
)

container.register(
    UpdatePageCommand,
    lambda scope, db: UpdatePageCommand(
        repository=scope.resolve(PageRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
        slug_uniqueness_service=scope.resolve(PageSlugUniquenessService, db=db),
    ),
)

container.register(
    DeletePageCommand,
    lambda scope, db: DeletePageCommand(
        repository=scope.resolve(PageRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    AddPageBlockCommand,
    lambda scope, db: AddPageBlockCommand(
        repository=scope.resolve(PageRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

# ==================== Commands: FAQ ====================

container.register(
    CreateFaqCommand,
    lambda scope, db: CreateFaqCommand(
        repository=scope.resolve(FaqRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateFaqCommand,
    lambda scope, db: UpdateFaqCommand(
        repository=scope.resolve(FaqRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteFaqCommand,
    lambda scope, db: DeleteFaqCommand(
        repository=scope.resolve(FaqRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

# ==================== Commands: Email Templates ====================

container.register(
    CreateEmailTemplateCommand,
    lambda scope, db: CreateEmailTemplateCommand(
        repository=scope.resolve(EmailTemplateRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateEmailTemplateCommand,
    lambda scope, db: UpdateEmailTemplateCommand(
        repository=scope.resolve(EmailTemplateRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteEmailTemplateCommand,
    lambda scope, db: DeleteEmailTemplateCommand(
        repository=scope.resolve(EmailTemplateRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

# ==================== Commands: Feature Flags ====================

container.register(
    CreateFeatureFlagCommand,
    lambda scope, db: CreateFeatureFlagCommand(
        repository=scope.resolve(FeatureFlagRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateFeatureFlagCommand,
    lambda scope, db: UpdateFeatureFlagCommand(
        repository=scope.resolve(FeatureFlagRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteFeatureFlagCommand,
    lambda scope, db: DeleteFeatureFlagCommand(
        repository=scope.resolve(FeatureFlagRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

# ==================== Commands: SEO ====================

container.register(
    CreateSeoCommand,
    lambda scope, db: CreateSeoCommand(
        repository=scope.resolve(SeoRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    UpdateSeoCommand,
    lambda scope, db: UpdateSeoCommand(
        repository=scope.resolve(SeoRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)

container.register(
    DeleteSeoCommand,
    lambda scope, db: DeleteSeoCommand(
        repository=scope.resolve(SeoRepository, db=db),
        uow=scope.resolve(UnitOfWork, db=db),
        event_bus=scope.resolve(AsyncEventBus, db=db),
    ),
)
