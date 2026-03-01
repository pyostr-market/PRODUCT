from typing import Optional


class BaseServiceError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
