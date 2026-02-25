from src.catalog.product.application.commands.create_product import CreateProductCommand
from src.catalog.product.application.commands.create_product_attribute import (
    CreateProductAttributeCommand,
)
from src.catalog.product.application.commands.create_product_type import (
    CreateProductTypeCommand,
)
from src.catalog.product.application.commands.delete_product import DeleteProductCommand
from src.catalog.product.application.commands.delete_product_attribute import (
    DeleteProductAttributeCommand,
)
from src.catalog.product.application.commands.delete_product_type import (
    DeleteProductTypeCommand,
)
from src.catalog.product.application.commands.update_product import UpdateProductCommand
from src.catalog.product.application.commands.update_product_attribute import (
    UpdateProductAttributeCommand,
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
from src.catalog.product.application.queries.product_type_admin_queries import (
    ProductTypeAdminQueries,
)
from src.catalog.product.application.queries.product_type_queries import (
    ProductTypeQueries,
)
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

    # ==================== ProductType ====================

    @staticmethod
    def build_create_product_type_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateProductTypeCommand, db=db)

    @staticmethod
    def build_update_product_type_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateProductTypeCommand, db=db)

    @staticmethod
    def build_delete_product_type_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteProductTypeCommand, db=db)

    @staticmethod
    def build_product_type_queries(db):
        scope = container.create_scope()
        return scope.resolve(ProductTypeQueries, db=db)

    @staticmethod
    def build_product_type_admin_queries(db):
        scope = container.create_scope()
        return scope.resolve(ProductTypeAdminQueries, db=db)

    # ==================== ProductAttribute ====================

    @staticmethod
    def build_create_product_attribute_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateProductAttributeCommand, db=db)

    @staticmethod
    def build_update_product_attribute_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateProductAttributeCommand, db=db)

    @staticmethod
    def build_delete_product_attribute_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteProductAttributeCommand, db=db)

    @staticmethod
    def build_product_attribute_queries(db):
        scope = container.create_scope()
        return scope.resolve(ProductAttributeQueries, db=db)
