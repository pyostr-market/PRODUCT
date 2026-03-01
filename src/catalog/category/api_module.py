from fastapi import FastAPI

from src.catalog.category.api.api_v1.admin import admin_category_router
from src.catalog.category.api.api_v1.pricing_policy_admin import (
    admin_pricing_policy_router,
)
from src.catalog.category.api.api_v1.commands import category_commands_router
from src.catalog.category.api.api_v1.pricing_policy_commands import (
    category_pricing_policy_commands_router,
)
from src.catalog.category.api.api_v1.pricing_policy_q import (
    category_pricing_policy_q_router,
)
from src.catalog.category.api.api_v1.q import category_q_router


class CategoryApiModule:
    name = "categories"
    order = 12
    mount_paths = ["/category"]

    def mount(self, app: FastAPI) -> None:
        app.include_router(category_q_router, prefix="/category")
        app.include_router(category_commands_router, prefix="/category")
        app.include_router(admin_category_router, prefix="/category/admin")

        # Category Pricing Policy routes
        app.include_router(
            category_pricing_policy_q_router,
            prefix="/category-pricing-policy",
        )
        app.include_router(
            category_pricing_policy_commands_router,
            prefix="/category-pricing-policy",
        )
        app.include_router(
            admin_pricing_policy_router,
            prefix="/category-pricing-policy/admin",
        )
