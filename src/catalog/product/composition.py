from src.catalog.product.application.commands.create_product import CreateProductCommand
from src.catalog.product.application.commands.delete_product import DeleteProductCommand
from src.catalog.product.application.commands.update_product import UpdateProductCommand
from src.catalog.product.application.queries.product_admin_queries import ProductAdminQueries
from src.catalog.product.application.queries.product_queries import ProductQueries
from src.catalog.product.container import container


class ProductComposition:

    @staticmethod
    def build_create_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateProductCommand, db=db)

    @staticmethod
    def build_update_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateProductCommand, db=db)

    @staticmethod
    def build_delete_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteProductCommand, db=db)

    @staticmethod
    def build_queries(db):
        scope = container.create_scope()
        return scope.resolve(ProductQueries, db=db)

    @staticmethod
    def build_admin_queries(db):
        scope = container.create_scope()
        return scope.resolve(ProductAdminQueries, db=db)
