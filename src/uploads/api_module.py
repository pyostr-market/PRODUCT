from src.core.api.module import ApiModule


class UploadsApiModule(ApiModule):
    """API модуль для загрузок файлов."""

    @property
    def name(self) -> str:
        return "uploads"

    @property
    def order(self) -> int:
        return 5  # Загрузки должны быть доступны до других модулей

    @property
    def source(self):
        return self

    @property
    def paths(self) -> list:
        return ["/upload"]

    def __init__(self):
        self._router = None

    @property
    def router(self):
        if self._router is None:
            from fastapi import APIRouter

            from src.uploads.api.api_v1.upload_api import upload_router
            self._router = APIRouter(prefix="/upload", tags=["Загрузка файлов"])
            self._router.include_router(upload_router)
        return self._router

    def mount(self, app):
        """Маунт роутера приложения."""
        app.include_router(self.router)
