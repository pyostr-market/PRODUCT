from fastapi import FastAPI

from src.core.api.system.docs import docs_router
from src.core.api.system.health import system_router


class CoreApiModule:
    name = "core"
    order = 0
    mount_paths = ["/system"]

    def mount(self, app: FastAPI) -> None:
        app.include_router(docs_router, prefix="/system")
        app.include_router(system_router, prefix="/system")
