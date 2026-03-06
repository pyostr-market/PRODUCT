import re
from dataclasses import dataclass

from src.catalog.suppliers.domain.exceptions import InvalidPhoneNumber


@dataclass(frozen=True)
class PhoneNumber:
    """
    Value Object для телефонного номера поставщика.

    Инварианты:
    - Номер должен содержать только цифры, +, -, (), пробелы
    - Минимальная длина: 10 символов (только цифры)
    - Максимальная длина: 20 символов
    """

    value: str

    def __post_init__(self):
        cleaned = self._clean_phone_number(self.value)

        if not self._is_valid_phone(cleaned):
            raise InvalidPhoneNumber()

        object.__setattr__(self, 'value', self.value.strip())

    @staticmethod
    def _clean_phone_number(phone: str) -> str:
        """Очистить номер от нецифровых символов."""
        return re.sub(r'[^\d]', '', phone)

    @staticmethod
    def _is_valid_phone(cleaned: str) -> bool:
        """Проверка валидности номера."""
        if len(cleaned) < 10 or len(cleaned) > 20:
            return False
        return True

    @classmethod
    def create(cls, value: str) -> 'PhoneNumber':
        """Создать PhoneNumber с валидацией."""
        return cls(value=value)

    @classmethod
    def create_optional(cls, value: str | None) -> 'PhoneNumber | None':
        """Создать optional PhoneNumber."""
        if not value:
            return None
        return cls(value=value)

    def cleaned(self) -> str:
        """Вернуть очищенный номер (только цифры)."""
        return self._clean_phone_number(self.value)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PhoneNumber):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
