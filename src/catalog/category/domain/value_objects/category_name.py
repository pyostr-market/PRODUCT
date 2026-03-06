from dataclasses import dataclass


class CategoryNameError(ValueError):
    """Базовое исключение для ошибок CategoryName."""
    pass


class InvalidCategoryName(CategoryNameError):
    """Некорректное имя категории."""

    def __init__(
        self,
        msg: str = "Некорректное имя категории",
        code: str = "invalid_category_name",
    ):
        super().__init__(f"{code}: {msg}")


@dataclass(frozen=True)
class CategoryName:
    """
    Value Object для представления имени категории.

    Инварианты:
    - Имя не может быть пустым
    - Минимальная длина - 2 символа
    - Максимальная длина - 255 символов
    """

    value: str

    def __post_init__(self):
        stripped = self.value.strip()

        if not stripped:
            raise InvalidCategoryName("Имя категории не может быть пустым")

        if len(stripped) < 2:
            raise InvalidCategoryName("Имя категории должно содержать не менее 2 символов")

        if len(stripped) > 255:
            raise InvalidCategoryName("Имя категории не может превышать 255 символов")

        object.__setattr__(self, 'value', stripped)

    @classmethod
    def create(cls, value: str) -> 'CategoryName':
        """Создать CategoryName из строки."""
        return cls(value=value)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CategoryName):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __len__(self) -> int:
        return len(self.value)
