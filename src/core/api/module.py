from abc import ABC, abstractmethod

from fastapi import APIRouter, FastAPI


class ApiModule(ABC):
    """Базовый класс для API модулей."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Имя модуля."""
        pass

    @property
    @abstractmethod
    def order(self) -> int:
        """Порядок загрузки модуля."""
        pass

    @property
    @abstractmethod
    def source(self):
        """Источник модуля (self)."""
        pass

    @property
    @abstractmethod
    def paths(self) -> list:
        """Список путей для маунта."""
        pass

    def mount(self, app: FastAPI) -> None:
        """Метод для маунта роутеров (опционально)."""
        pass

    def configure_routers(self) -> None:
        """Настройка роутеров модуля."""
        pass

    @property
    def router(self) -> APIRouter:
        """Возвращает роутер модуля."""
        return APIRouter()
