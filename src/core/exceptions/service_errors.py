from src.core.exceptions.base import BaseServiceError


class ConflictError(BaseServiceError):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="conflict",
            status_code=409,
        )