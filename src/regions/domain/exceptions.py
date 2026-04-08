from src.core.exceptions.base import BaseServiceError


class RegionNotFound(BaseServiceError):
    """Регион не найден."""

    def __init__(
        self,
        msg: str = 'Регион не найден',
        code: str = 'region_not_found',
        status_code: int = 404,
    ):
        super().__init__(
            message=msg,
            code=code,
            status_code=status_code,
        )


class RegionAlreadyExists(BaseServiceError):
    """Регион уже существует."""

    def __init__(
        self,
        msg: str = 'Регион уже существует',
        code: str = 'region_already_exists',
        status_code: int = 409,
    ):
        super().__init__(
            message=msg,
            code=code,
            status_code=status_code,
        )


class RegionNameTooShort(BaseServiceError):
    """Имя региона слишком короткое."""

    def __init__(
        self,
        msg: str = 'Имя региона должно содержать минимум 2 символа',
        code: str = 'region_name_too_short',
        status_code: int = 400,
    ):
        super().__init__(
            message=msg,
            code=code,
            status_code=status_code,
        )
