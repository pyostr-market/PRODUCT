from fastapi import Request

import src.mount_models
from src.core.api.fastapi_conf import app_server
from src.core.api.responses import api_response
from src.core.exceptions.base import BaseServiceError
from src.core.loader.module_loader import mount_all
from src.core.logs.logging_config import setup_logging

setup_logging()


def create_app():
    mount_all(app_server)
    return app_server


app = create_app()

@app.exception_handler(BaseServiceError)
async def service_error_handler(request: Request, exc: BaseServiceError):
    return api_response(exc)