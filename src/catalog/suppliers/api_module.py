from fastapi import FastAPI

from src.catalog.suppliers.api.api_v1.admin import admin_supplier_router
from src.catalog.suppliers.api.api_v1.commands import supplier_commands_router
from src.catalog.suppliers.api.api_v1.q import supplier_q_router


class SupplierApiModule:
    name = "suppliers"
    order = 11
    mount_paths = ["/supplier"]

    def mount(self, app: FastAPI) -> None:
        app.include_router(supplier_q_router, prefix="/supplier")
        app.include_router(supplier_commands_router, prefix="/supplier")
        app.include_router(admin_supplier_router, prefix="/supplier/admin")
