from src.catalog.suppliers.application.commands.create_supplier import CreateSupplierCommand
from src.catalog.suppliers.application.commands.update_supplier import UpdateSupplierCommand
from src.catalog.suppliers.application.commands.delete_supplier import DeleteSupplierCommand
from src.catalog.suppliers.application.queries.supplier_admin_queries import SupplierAdminQueries
from src.catalog.suppliers.application.queries.supplier_queries import SupplierQueries
from src.catalog.suppliers.container import container


class SupplierComposition:

    @staticmethod
    def build_create_command(db):
        scope = container.create_scope()
        return scope.resolve(CreateSupplierCommand, db=db)

    @staticmethod
    def build_update_command(db):
        scope = container.create_scope()
        return scope.resolve(UpdateSupplierCommand, db=db)

    @staticmethod
    def build_delete_command(db):
        scope = container.create_scope()
        return scope.resolve(DeleteSupplierCommand, db=db)

    @staticmethod
    def build_queries(db):
        scope = container.create_scope()
        return scope.resolve(SupplierQueries, db=db)

    @staticmethod
    def build_admin_queries(db):
        scope = container.create_scope()
        return scope.resolve(SupplierAdminQueries, db=db)
