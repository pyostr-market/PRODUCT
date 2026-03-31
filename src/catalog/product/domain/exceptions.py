from src.catalog.product.domain.value_objects.product_name import ProductNameTooShort
from src.core.exceptions.base import BaseServiceError


class ProductNotFound(BaseServiceError):
    def __init__(
        self,
        msg: str = "Товар не найден",
        code: str = "product_not_found",
        status_code: int = 404,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductInvalidImage(BaseServiceError):
    def __init__(
        self,
        msg: str = "Передан невалидный файл изображения",
        code: str = "product_invalid_image",
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message=msg, code=code, status_code=status_code, details=details)


class ProductRelatedLookupRequired(BaseServiceError):
    def __init__(
        self,
        msg: str = "Нужно передать product_id или name",
        code: str = "product_related_lookup_required",
        status_code: int = 400,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductInvalidPayload(BaseServiceError):
    def __init__(
        self,
        msg: str = "Некорректные данные запроса",
        code: str = "product_invalid_payload",
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message=msg, code=code, status_code=status_code, details=details)


class ProductTypeNotFound(BaseServiceError):
    def __init__(
        self,
        msg: str = "Тип продукта не найден",
        code: str = "product_type_not_found",
        status_code: int = 404,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductTypeAlreadyExists(BaseServiceError):
    def __init__(
        self,
        msg: str = "Тип продукта уже существует",
        code: str = "product_type_already_exists",
        status_code: int = 409,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductTypeInvalidName(BaseServiceError):
    def __init__(
        self,
        msg: str = "Имя слишком короткое",
        code: str = "product_type_invalid_name",
        status_code: int = 400,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductAttributeNotFound(BaseServiceError):
    def __init__(
        self,
        msg: str = "Атрибут продукта не найден",
        code: str = "product_attribute_not_found",
        status_code: int = 404,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductAttributeAlreadyExists(BaseServiceError):
    def __init__(
        self,
        msg: str = "Атрибут продукта уже существует",
        code: str = "product_attribute_already_exists",
        status_code: int = 409,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductAttributeInvalidName(BaseServiceError):
    def __init__(
        self,
        msg: str = "Имя слишком короткое",
        code: str = "product_attribute_invalid_name",
        status_code: int = 400,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductRelationNotFound(BaseServiceError):
    def __init__(
        self,
        msg: str = "Связь товара не найдена",
        code: str = "product_relation_not_found",
        status_code: int = 404,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductRelationAlreadyExists(BaseServiceError):
    def __init__(
        self,
        msg: str = "Связь уже существует",
        code: str = "product_relation_already_exists",
        status_code: int = 409,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductRelationSelfReference(BaseServiceError):
    def __init__(
        self,
        msg: str = "Связь товара с самим собой не допускается",
        code: str = "product_relation_self_reference",
        status_code: int = 400,
    ):
        super().__init__(message=msg, code=code, status_code=status_code)


class ProductRelationInvalidProduct(BaseServiceError):
    def __init__(
        self,
        msg: str = "Один из товаров не существует",
        code: str = "product_relation_invalid_product",
        status_code: int = 400,
        details: dict | None = None,
    ):
        super().__init__(message=msg, code=code, status_code=status_code, details=details)
