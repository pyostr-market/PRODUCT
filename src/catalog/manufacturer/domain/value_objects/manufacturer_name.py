from dataclasses import dataclass

from src.catalog.manufacturer.domain.exceptions import ManufacturerNameTooShort


@dataclass(frozen=True)
class ManufacturerName:
    """
    Value Object для имени производителя.

    Инварианты:
    - Имя не может быть пустым
    - Минимальная длина: 2 символа
    - Имя нормализуется (trim)
    """

    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 2:
            raise ManufacturerNameTooShort()
        object.__setattr__(self, 'value', self.value.strip())

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManufacturerName):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
