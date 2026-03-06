from dataclasses import dataclass


@dataclass(frozen=True)
class ProductId:
    """
    Value Object для идентификации продукта.
    """
    value: int

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProductId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProductTypeId:
    """
    Value Object для идентификации типа продукта.
    """
    value: int

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProductTypeId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


@dataclass(frozen=True)
class ProductAttributeId:
    """
    Value Object для идентификации атрибута продукта.
    """
    value: int

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProductAttributeId):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)
