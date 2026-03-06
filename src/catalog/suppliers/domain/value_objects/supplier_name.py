from src.catalog.suppliers.domain.exceptions import (
    InvalidContactEmail,
    InvalidPhoneNumber,
    SupplierNameTooLong,
    SupplierNameTooShort,
)


class SupplierName:
    """
    Value Object для имени поставщика.

    Инварианты:
    - Имя не может быть пустым
    - Минимальная длина: 2 символа
    - Максимальная длина: 150 символов
    - Имя нормализуется (trim)
    """

    def __init__(
        self,
        value: str,
        min_length: int = 2,
        max_length: int = 150,
    ):
        normalized = value.strip() if value else ""

        if len(normalized) < min_length:
            raise SupplierNameTooShort()

        if len(normalized) > max_length:
            raise SupplierNameTooLong()

        self._value = normalized
        self._min_length = min_length
        self._max_length = max_length

    @classmethod
    def create(cls, value: str) -> 'SupplierName':
        """Создать SupplierName с валидацией."""
        return cls(value=value)

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SupplierName):
            return NotImplemented
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __len__(self) -> int:
        return len(self._value)

    @property
    def value(self) -> str:
        """Вернуть значение имени."""
        return self._value
