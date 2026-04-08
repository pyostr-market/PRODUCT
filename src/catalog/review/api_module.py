"""API модуль для отзывов."""

from fastapi import FastAPI

from src.catalog.review.api.api_v1.admin import review_admin_router
from src.catalog.review.api.api_v1.commands import review_commands_router
from src.catalog.review.api.api_v1.q import review_queries_router


class ReviewApiModule:
    name = "reviews"
    order = 15
    mount_paths = ["/reviews"]

    def mount(self, app: FastAPI) -> None:
        app.include_router(review_queries_router, prefix="/reviews")
        app.include_router(review_commands_router, prefix="/reviews")
        app.include_router(review_admin_router, prefix="/reviews/admin")
