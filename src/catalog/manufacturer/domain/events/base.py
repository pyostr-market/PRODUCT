from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class DomainEvent:
    """Базовый класс для всех доменных событий."""
    
    def to_dict(self) -> dict[str, Any]:
        """Сериализовать событие в словарь."""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }
