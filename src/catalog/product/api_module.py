from fastapi import FastAPI

from src.catalog.product.api.api_v1.admin import admin_product_router, admin_product_type_router
from src.catalog.product.api.api_v1.commands import product_commands_router
from src.catalog.product.api.api_v1.product_attribute_commands import product_attribute_commands_router
from src.catalog.product.api.api_v1.product_type_commands import product_type_commands_router
from src.catalog.product.api.api_v1.q import product_q_router, product_type_q_router


class ProductApiModule:
    name = "products"
    order = 11
    mount_paths = ["/product"]

    def mount(self, app: FastAPI) -> None:
        app.include_router(product_q_router, prefix="/product")
        app.include_router(product_type_q_router, prefix="/product")
        app.include_router(product_commands_router, prefix="/product")
        app.include_router(product_type_commands_router, prefix="/product")
        app.include_router(product_attribute_commands_router, prefix="/product")
        app.include_router(admin_product_router, prefix="/product/admin")
        app.include_router(admin_product_type_router, prefix="/product/admin")
