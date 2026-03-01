from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EventPublisher(ABC):

    @abstractmethod
    async def publish(self, message: dict[str, Any]) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        return None


class NullEventPublisher(EventPublisher):

    async def publish(self, message: dict[str, Any]) -> None:
        return None
