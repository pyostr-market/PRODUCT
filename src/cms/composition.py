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
from src.cms.container import container


class CmsComposition:
    """Composition root для CMS модуля."""

    @staticmethod
    def build_create_page_command(db):
        scope = container.create_scope()
        return scope.resolve(CreatePageCommand, db=db)

    @staticmethod
    def build_update_page_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdatePageCommand, db=db)

    @staticmethod
    def build_delete_page_command(db):
        scope = container.create_scope()
        return scope.resolve(DeletePageCommand, db=db)

    @staticmethod
    def build_add_page_block_command(db):
        scope = container.create_scope()
        return scope.resolve(AddPageBlockCommand, db=db)

    @staticmethod
    def build_page_queries(db):
        scope = container.create_scope()
        return scope.resolve(PageQueries, db=db)

    @staticmethod
    def build_create_faq_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateFaqCommand, db=db)

    @staticmethod
    def build_update_faq_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateFaqCommand, db=db)

    @staticmethod
    def build_delete_faq_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteFaqCommand, db=db)

    @staticmethod
    def build_faq_queries(db):
        scope = container.create_scope()
        return scope.resolve(FaqQueries, db=db)

    @staticmethod
    def build_create_email_template_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateEmailTemplateCommand, db=db)

    @staticmethod
    def build_update_email_template_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateEmailTemplateCommand, db=db)

    @staticmethod
    def build_delete_email_template_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteEmailTemplateCommand, db=db)

    @staticmethod
    def build_email_template_queries(db):
        scope = container.create_scope()
        return scope.resolve(EmailTemplateQueries, db=db)

    @staticmethod
    def build_create_feature_flag_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateFeatureFlagCommand, db=db)

    @staticmethod
    def build_update_feature_flag_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateFeatureFlagCommand, db=db)

    @staticmethod
    def build_delete_feature_flag_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteFeatureFlagCommand, db=db)

    @staticmethod
    def build_feature_flag_queries(db):
        scope = container.create_scope()
        return scope.resolve(FeatureFlagQueries, db=db)

    @staticmethod
    def build_create_seo_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateSeoCommand, db=db)

    @staticmethod
    def build_update_seo_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateSeoCommand, db=db)

    @staticmethod
    def build_delete_seo_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteSeoCommand, db=db)

    @staticmethod
    def build_seo_queries(db):
        scope = container.create_scope()
        return scope.resolve(SeoQueries, db=db)
