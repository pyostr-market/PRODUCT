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


class CategoryInvalidImage(BaseServiceError):
    def __init__(
        self,
        msg: str = "Передан невалидный файл изображения",
        code: str = "category_invalid_image",
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message=msg, code=code, status_code=status_code, details=details)


class CategoryImagesOrderingMismatch(BaseServiceError):
    def __init__(
        self,
        msg: str = "Количество изображений и ordering не совпадает",
        code: str = "category_images_ordering_mismatch",
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message=msg, code=code, status_code=status_code, details=details)


class CategoryPricingPolicyNotFound(BaseServiceError):
    def __init__(
        self,
        msg: str = "Политика ценообразования категории не найдена",
        code: str = "category_pricing_policy_not_found",
        status_code: int = 404,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class CategoryPricingPolicyInvalidData(BaseServiceError):
    def __init__(
        self,
        msg: str = "Некорректные данные политики ценообразования",
        code: str = "category_pricing_policy_invalid_data",
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message=msg, code=code, status_code=status_code, details=details)


class CategoryPricingPolicyAlreadyExists(BaseServiceError):
    def __init__(
        self,
        msg: str = "Политика ценообразования для этой категории уже существует",
        code: str = "category_pricing_policy_already_exists",
        status_code: int = 409,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class CategoryPricingPolicyCategoryNotFound(BaseServiceError):
    def __init__(
        self,
        msg: str = "Категория для политики ценообразования не найдена",
        code: str = "category_pricing_policy_category_not_found",
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message=msg, code=code, status_code=status_code, details=details)


class CategoryPricingPolicyInvalidRateValue(BaseServiceError):
    def __init__(
        self,
        msg: str = "Некорректное значение ставки (должно быть от 0 до 100)",
        code: str = "category_pricing_policy_invalid_rate_value",
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message=msg, code=code, status_code=status_code, details=details)
