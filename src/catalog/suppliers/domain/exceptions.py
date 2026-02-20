from src.core.exceptions.base import BaseServiceError


class SupplierAlreadyExists(BaseServiceError):
    def __init__(
        self,
        msg: str = "Поставщик уже существует",
        code: str = "supplier_already_exist",
        status_code: int = 409,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class SupplierNotFound(BaseServiceError):
    def __init__(
        self,
        msg: str = "Поставщик не найден",
        code: str = "supplier_not_found",
        status_code: int = 404,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class SupplierNameTooShort(BaseServiceError):
    def __init__(
        self,
        msg: str = "Имя слишком короткое",
        code: str = "supplier_name_too_short",
        status_code: int = 400,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)
