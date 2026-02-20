from fastapi import FastAPI

from src.catalog.manufacturer.api.api_v1.admin import admin_manufacturer_router
from src.catalog.manufacturer.api.api_v1.commands import manufacturer_commands_router
from src.catalog.manufacturer.api.api_v1.q import manufacturer_q_router


class ManufacturerApiModule:
    name = "manufacturers"
    order = 10
    mount_paths = ["/manufacturer",]

    def mount(self, app: FastAPI) -> None:
        app.include_router(manufacturer_q_router, prefix="/manufacturer")
        app.include_router(manufacturer_commands_router, prefix="/manufacturer")
        app.include_router(admin_manufacturer_router, prefix="/manufacturer/admin")