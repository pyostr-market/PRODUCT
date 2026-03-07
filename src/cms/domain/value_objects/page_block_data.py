from dataclasses import dataclass
from typing import Any


@dataclass
class PageBlockData:
    """Value object для данных блока страницы."""
    data: dict[str, Any]

    def __post_init__(self):
        if not isinstance(self.data, dict):
            raise ValueError("Данные блока должны быть словарем")
