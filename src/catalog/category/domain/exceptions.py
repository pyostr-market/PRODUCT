from src.core.exceptions.base import BaseServiceError


class CategoryNotFound(BaseServiceError):
    def __init__(
        self,
        msg: str = "Категория не найдена",
        code: str = "category_not_found",
        status_code: int = 404,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class CategoryNameTooShort(BaseServiceError):
    def __init__(
        self,
        msg: str = "Имя слишком короткое",
        code: str = "category_name_too_short",
        status_code: int = 400,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)
