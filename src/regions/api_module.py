from fastapi import FastAPI

from src.regions.api.api_v1.admin import admin_region_router
from src.regions.api.api_v1.commands import region_commands_router
from src.regions.api.api_v1.q import region_q_router


class RegionApiModule:
    name = "regions"
    order = 5
    mount_paths = ["/region"]

    def mount(self, app: FastAPI) -> None:
        app.include_router(region_q_router, prefix="/region")
        app.include_router(region_commands_router, prefix="/region")
        app.include_router(admin_region_router, prefix="/region/admin")
