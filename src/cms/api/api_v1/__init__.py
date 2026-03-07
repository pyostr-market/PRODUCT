# API v1 for CMS

from src.cms.api.api_v1.admin import admin_page_router
from src.cms.api.api_v1.commands import page_commands_router
from src.cms.api.api_v1.q import page_q_router

__all__ = [
    "admin_page_router",
    "page_commands_router",
    "page_q_router",
]
