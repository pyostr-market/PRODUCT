from dataclasses import dataclass


@dataclass(frozen=True)
class CategoryId:
    """
    Value Object для идентификации категории.
    
    Используется для защиты от случайного смешивания ID разных сущностей.
    """
    value: int

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CategoryId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ManufacturerId:
    """
    Value Object для идентификации производителя.
    """
    value: int

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManufacturerId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class PricingPolicyId:
    """
    Value Object для идентификации политики ценообразования.
    """
    value: int

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PricingPolicyId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
