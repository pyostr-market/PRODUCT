import re
from dataclasses import dataclass

from src.catalog.suppliers.domain.exceptions import InvalidContactEmail


@dataclass(frozen=True)
class ContactEmail:
    """
    Value Object для контактного email поставщика.

    Инварианты:
    - Email должен быть валидным форматом
    - Email не может быть пустым (но может быть None в агрегате)
    """

    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise InvalidContactEmail()

        object.__setattr__(self, 'value', self.value.lower().strip())

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Проверка валидности email."""
        if not email:
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @classmethod
    def create(cls, value: str) -> 'ContactEmail':
        """Создать ContactEmail с валидацией."""
        return cls(value=value)

    @classmethod
    def create_optional(cls, value: str | None) -> 'ContactEmail | None':
        """Создать optional ContactEmail."""
        if not value:
            return None
        return cls(value=value)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ContactEmail):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
