from src.catalog.category.application.commands.create_category import (
    CreateCategoryCommand,
)
from src.catalog.category.application.commands.create_pricing_policy import (
    CreateCategoryPricingPolicyCommand,
)
from src.catalog.category.application.commands.delete_category import (
    DeleteCategoryCommand,
)
from src.catalog.category.application.commands.delete_pricing_policy import (
    DeleteCategoryPricingPolicyCommand,
)
from src.catalog.category.application.commands.update_category import (
    UpdateCategoryCommand,
)
from src.catalog.category.application.commands.update_pricing_policy import (
    UpdateCategoryPricingPolicyCommand,
)
from src.catalog.category.application.queries.category_admin_queries import (
    CategoryAdminQueries,
)
from src.catalog.category.application.queries.category_queries import CategoryQueries
from src.catalog.category.application.queries.pricing_policy_queries import (
    CategoryPricingPolicyQueries,
)
from src.catalog.category.container import container


class CategoryComposition:

    @staticmethod
    def build_create_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateCategoryCommand, db=db)

    @staticmethod
    def build_update_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateCategoryCommand, db=db)

    @staticmethod
    def build_delete_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteCategoryCommand, db=db)

    @staticmethod
    def build_queries(db):
        scope = container.create_scope()
        return scope.resolve(CategoryQueries, db=db)

    @staticmethod
    def build_admin_queries(db):
        scope = container.create_scope()
        return scope.resolve(CategoryAdminQueries, db=db)


class CategoryPricingPolicyComposition:

    @staticmethod
    def build_create_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateCategoryPricingPolicyCommand, db=db)

    @staticmethod
    def build_update_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateCategoryPricingPolicyCommand, db=db)

    @staticmethod
    def build_delete_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteCategoryPricingPolicyCommand, db=db)

    @staticmethod
    def build_queries(db):
        scope = container.create_scope()
        return scope.resolve(CategoryPricingPolicyQueries, db=db)
