from decimal import Decimal, InvalidOperation
from dataclasses import dataclass


class PercentageError(ValueError):
    """Базовое исключение для ошибок Percentage."""
    pass


class InvalidPercentageAmount(PercentageError):
    """Некорректное значение процента."""

    def __init__(
        self,
        msg: str = "Некорректное значение процента",
        code: str = "invalid_percentage_amount",
    ):
        super().__init__(f"{code}: {msg}")


@dataclass(frozen=True)
class Percentage:
    """
    Value Object для представления процентного значения.

    Инварианты:
    - Процент должен быть в диапазоне от 0 до 100
    - Значение хранится с точностью до 2 знаков после запятой
    """

    value: Decimal

    def __post_init__(self):
        if self.value < Decimal("0") or self.value > Decimal("100"):
            raise InvalidPercentageAmount(
                f"Процент должен быть в диапазоне от 0 до 100: {self.value}"
            )

        # Нормализуем до 2 знаков после запятой
        object.__setattr__(self, 'value', self.value.quantize(Decimal('0.01')))

    @classmethod
    def from_decimal(cls, value: Decimal | str | int | float) -> 'Percentage':
        """Создать Percentage из Decimal, строки, int или float."""
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError) as e:
            raise InvalidPercentageAmount(f"Некорректный формат процента: {value}") from e

        return cls(value=decimal_value)

    @classmethod
    def zero(cls) -> 'Percentage':
        """Создать Percentage с нулевым значением."""
        return cls(value=Decimal('0.00'))

    @classmethod
    def hundred(cls) -> 'Percentage':
        """Создать Percentage со значением 100."""
        return cls(value=Decimal('100.00'))

    def __add__(self, other: 'Percentage') -> 'Percentage':
        if not isinstance(other, Percentage):
            return NotImplemented
        result = self.value + other.value
        if result > Decimal("100"):
            raise InvalidPercentageAmount(f"Результат сложения не может быть больше 100: {result}")
        return Percentage(value=result)

    def __sub__(self, other: 'Percentage') -> 'Percentage':
        if not isinstance(other, Percentage):
            return NotImplemented
        result = self.value - other.value
        if result < Decimal("0"):
            raise InvalidPercentageAmount(f"Результат вычитания не может быть меньше 0: {result}")
        return Percentage(value=result)

    def __mul__(self, factor: Decimal | int | float) -> 'Percentage':
        try:
            decimal_factor = Decimal(str(factor))
        except (InvalidOperation, ValueError) as e:
            raise InvalidPercentageAmount(f"Некорректный множитель: {factor}") from e

        if decimal_factor < 0:
            raise InvalidPercentageAmount(f"Множитель не может быть отрицательным: {decimal_factor}")

        result = self.value * decimal_factor
        if result > Decimal("100"):
            raise InvalidPercentageAmount(f"Результат умножения не может быть больше 100: {result}")

        return Percentage(value=result)

    def __lt__(self, other: 'Percentage') -> bool:
        if not isinstance(other, Percentage):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other: 'Percentage') -> bool:
        if not isinstance(other, Percentage):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other: 'Percentage') -> bool:
        if not isinstance(other, Percentage):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other: 'Percentage') -> bool:
        if not isinstance(other, Percentage):
            return NotImplemented
        return self.value >= other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Percentage):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return f"{self.value}%"

    def to_decimal(self) -> Decimal:
        """Вернуть значение как Decimal."""
        return self.value

    def apply_to(self, amount: Decimal) -> Decimal:
        """Применить процент к сумме."""
        return amount * (self.value / Decimal("100"))
