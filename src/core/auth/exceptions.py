from src.core.exceptions.base import BaseServiceError


class UnauthorizedError(BaseServiceError):
    def __init__(self, message: str = "Не авторизован"):
        super().__init__(
            message=message,
            code="unauthorized",
            status_code=401,
        )


class ForbiddenError(BaseServiceError):
    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(
            message=message,
            code="forbidden",
            status_code=403,
        )