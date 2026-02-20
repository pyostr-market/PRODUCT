from src.core.exceptions.base import BaseServiceError


class ManufacturerAlreadyExists(BaseServiceError):
    def __init__(
            self,
            msg: str = 'Производитель уже существует',
            code: str = 'manufacturer_already_exist',
            status_code: int = 409,
    ):
        super().__init__(
            message=msg,
            code=code,
            status_code=status_code,
        )


class ManufacturerNotFound(BaseServiceError):
    def __init__(
            self,
            msg: str = 'Производитель не найден',
            code: str = 'manufacturer_not_found',
            status_code: int = 404,
    ):
        super().__init__(
            message=msg,
            code=code,
            status_code=status_code,
        )

class ManufacturerNameTooShort(BaseServiceError):
    def __init__(
            self,
            msg: str = 'Имя слишком короткое',
            code: str = 'manufacturer_name_too_short',
            status_code: int = 400,
    ):
        super().__init__(
            message=msg,
            code=code,
            status_code=status_code,
        )