from dataclasses import dataclass
from typing import Optional


@dataclass
class TagAggregate:
    """Доменная модель тега."""
    tag_id: int
    name: str
    description: Optional[str] = None

    def update(self, name: Optional[str] = None, description: Optional[str] = None) -> None:
        """Обновить данные тега."""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
