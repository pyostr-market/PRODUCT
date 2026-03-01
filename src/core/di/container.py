from threading import Lock
from typing import Any, Callable, Dict


class ServiceContainer:
    def __init__(self):
        self._factories: Dict[Any, Callable[..., Any]] = {}
        self._lock = Lock()

    def register(self, key: Any, factory: Callable[..., Any]) -> None:
        with self._lock:
            if key in self._factories:
                raise ValueError(f"Service '{key}' already registered")
            self._factories[key] = factory

    def create_scope(self):
        return ServiceScope(self._factories)


class ServiceScope:
    def __init__(self, factories: Dict[Any, Callable[..., Any]]):
        self._factories = factories
        self._instances: Dict[Any, Any] = {}

    def resolve(self, key: Any, **kwargs):
        if key not in self._instances:
            if key not in self._factories:
                raise KeyError(f"Service '{key}' not registered")

            self._instances[key] = self._factories[key](self, **kwargs)

        return self._instances[key]