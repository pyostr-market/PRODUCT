from decimal import Decimal, InvalidOperation
from dataclasses import dataclass


class MoneyError(ValueError):
    """Базовое исключение для ошибок Money."""
    pass


class InvalidMoneyAmount(MoneyError):
    """Некорректная сумма денег."""
    
    def __init__(
        self,
        msg: str = "Некорректная сумма денег",
        code: str = "invalid_money_amount",
    ):
        super().__init__(f"{code}: {msg}")


@dataclass(frozen=True)
class Money:
    """
    Value Object для представления денежной суммы.
    
    Инварианты:
    - Сумма не может быть отрицательной
    - Сумма хранится с точностью до 2 знаков после запятой
    """
    
    amount: Decimal
    
    def __post_init__(self):
        if self.amount < 0:
            raise InvalidMoneyAmount(f"Сумма не может быть отрицательной: {self.amount}")
        
        # Нормализуем до 2 знаков после запятой
        object.__setattr__(self, 'amount', self.amount.quantize(Decimal('0.01')))
    
    @classmethod
    def from_decimal(cls, amount: Decimal | str | int | float) -> 'Money':
        """Создать Money из Decimal, строки, int или float."""
        try:
            decimal_amount = Decimal(str(amount))
        except (InvalidOperation, ValueError) as e:
            raise InvalidMoneyAmount(f"Некорректный формат суммы: {amount}") from e
        
        return cls(amount=decimal_amount)
    
    @classmethod
    def zero(cls) -> 'Money':
        """Создать Money с нулевой суммой."""
        return cls(amount=Decimal('0.00'))
    
    def __add__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            return NotImplemented
        return Money(amount=self.amount + other.amount)
    
    def __sub__(self, other: 'Money') -> 'Money':
        if not isinstance(other, Money):
            return NotImplemented
        result = self.amount - other.amount
        if result < 0:
            raise InvalidMoneyAmount(f"Результат вычитания не может быть отрицательным: {result}")
        return Money(amount=result)
    
    def __mul__(self, factor: Decimal | int | float) -> 'Money':
        try:
            decimal_factor = Decimal(str(factor))
        except (InvalidOperation, ValueError) as e:
            raise InvalidMoneyAmount(f"Некорректный множитель: {factor}") from e
        
        if decimal_factor < 0:
            raise InvalidMoneyAmount(f"Множитель не может быть отрицательным: {decimal_factor}")
        
        return Money(amount=self.amount * decimal_factor)
    
    def __lt__(self, other: 'Money') -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount
    
    def __le__(self, other: 'Money') -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount <= other.amount
    
    def __gt__(self, other: 'Money') -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount > other.amount
    
    def __ge__(self, other: 'Money') -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount >= other.amount
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount
    
    def __hash__(self) -> int:
        return hash(self.amount)
    
    def __str__(self) -> str:
        return str(self.amount)
    
    def to_decimal(self) -> Decimal:
        """Вернуть сумму как Decimal."""
        return self.amount
