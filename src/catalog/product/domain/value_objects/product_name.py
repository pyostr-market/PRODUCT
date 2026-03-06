from src.core.exceptions.base import BaseServiceError


class ProductNameError(BaseServiceError):
    """Базовое исключение для ошибок ProductName."""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message=message, code=code, status_code=status_code, details=details)


class InvalidProductName(ProductNameError):
    """Некорректное имя продукта."""
    
    def __init__(
        self,
        message: str = "Некорректное имя продукта",
        code: str = "invalid_product_name",
        status_code: int = 400,
        details: dict | None = None,
    ):
        # Вызываем напрямую BaseServiceError, минуя MRO
        BaseServiceError.__init__(
            self,
            message=message,
            code=code,
            status_code=status_code,
            details=details,
        )


class ProductNameTooShort(InvalidProductName):
    """Имя продукта слишком короткое."""
    
    def __init__(
        self,
        min_length: int = 2,
    ):
        message = f"Имя продукта должно содержать минимум {min_length} символов"
        # Вызываем напрямую BaseServiceError, минуя MRO
        BaseServiceError.__init__(
            self,
            message=message,
            code="product_name_too_short",
        )


class ProductNameTooLong(InvalidProductName):
    """Имя продукта слишком длинное."""
    
    def __init__(
        self,
        max_length: int = 200,
    ):
        message = f"Имя продукта не может превышать {max_length} символов"
        BaseServiceError.__init__(
            self,
            message=message,
            code="product_name_too_long",
        )


class ProductName:
    """
    Value Object для имени продукта.
    
    Инварианты:
    - Имя должно содержать минимум 2 символа
    - Имя не может превышать 200 символов
    - Имя хранится в нормализованном виде (trimmed)
    """
    
    def __init__(
        self,
        value: str,
        min_length: int = 2,
        max_length: int = 200,
    ):
        normalized = value.strip() if value else ""
        
        if len(normalized) < min_length:
            raise ProductNameTooShort(min_length)
        
        if len(normalized) > max_length:
            raise ProductNameTooLong(max_length)
        
        self._value = normalized
        self._min_length = min_length
        self._max_length = max_length
    
    @classmethod
    def create(cls, value: str) -> 'ProductName':
        """Создать ProductName с валидацией."""
        return cls(value=value)
    
    def __str__(self) -> str:
        return self._value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProductName):
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
