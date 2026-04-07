from fastapi import FastAPI

from src.catalog.product.api.api_v1.admin import (
    admin_product_router,
    admin_product_type_router,
)
from src.catalog.product.api.api_v1.commands import product_commands_router
from src.catalog.product.api.api_v1.product_attribute_commands import (
    product_attribute_commands_router,
)
from src.catalog.product.api.api_v1.product_attribute_q import (
    product_attribute_q_router,
)
from src.catalog.product.api.api_v1.product_relation_commands import (
    product_relation_commands_router,
    product_relation_q_router,
)
from src.catalog.product.api.api_v1.product_type_commands import (
    product_type_commands_router,
)
from src.catalog.product.api.api_v1.q import product_q_router, product_type_q_router
from src.catalog.product.api.api_v1.tag_commands import tag_router


class ProductApiModule:
    name = "products"
    order = 11
    mount_paths = ["/product"]

    def mount(self, app: FastAPI) -> None:
        # Сначала специфичные маршруты (type, attribute, relation), потом общие ({product_id})
        app.include_router(product_type_q_router, prefix="/product")
        app.include_router(product_type_commands_router, prefix="/product")
        app.include_router(product_attribute_q_router, prefix="/product")
        app.include_router(product_attribute_commands_router, prefix="/product")
        # Product relations — отдельные пути для команд и query
        app.include_router(product_relation_commands_router, prefix="/product/product-relations")
        app.include_router(product_relation_q_router, prefix="/product")
        # Product tags
        app.include_router(tag_router, prefix="/product")
        app.include_router(product_q_router, prefix="/product")
        app.include_router(product_commands_router, prefix="/product")
        app.include_router(admin_product_router, prefix="/product/admin")
        app.include_router(admin_product_type_router, prefix="/product/admin")
