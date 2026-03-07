# Domain exceptions for CMS

from src.core.exceptions.base import BaseServiceError


class CmsError(BaseServiceError):
    """Базовое исключение для CMS модуля."""
    
    def __init__(self, message: str, code: str = "cms_error", status_code: int = 400, details: dict | None = None):
        super().__init__(message=message, code=code, status_code=status_code, details=details or {})


class PageNotFound(CmsError):
    """Страница не найдена."""

    def __init__(self, slug: str | None = None):
        self.slug = slug
        message = f"Страница не найдена"
        if slug:
            message += f": {slug}"
        super().__init__(message=message, code="page_not_found", status_code=404)


class PageSlugAlreadyExists(CmsError):
    """Slug страницы уже существует."""

    def __init__(self, slug: str):
        self.slug = slug
        super().__init__(message=f"Страница с slug '{slug}' уже существует", code="page_slug_exists", status_code=400)


class PageSlugInvalid(CmsError):
    """Некорректный формат slug."""

    def __init__(self):
        super().__init__(message="Некорректный формат slug. Допустимы только буквы, цифры, дефисы и подчеркивания", code="page_slug_invalid", status_code=400)


class PageBlockNotFound(CmsError):
    """Блок страницы не найден."""

    def __init__(self, block_id: int):
        self.block_id = block_id
        super().__init__(message=f"Блок страницы не найден: {block_id}", code="page_block_not_found", status_code=404)


class PageBlockTypeInvalid(CmsError):
    """Некорректный тип блока."""

    def __init__(self, block_type: str):
        self.block_type = block_type
        super().__init__(message=f"Некорректный тип блока: {block_type}", code="page_block_type_invalid", status_code=400)


class FaqNotFound(CmsError):
    """FAQ не найден."""

    def __init__(self, faq_id: int | None = None):
        self.faq_id = faq_id
        message = "FAQ не найден"
        if faq_id:
            message += f": {faq_id}"
        super().__init__(message=message, code="faq_not_found", status_code=404)


class EmailTemplateNotFound(CmsError):
    """Email шаблон не найден."""

    def __init__(self, key: str | None = None):
        self.key = key
        message = "Email шаблон не найден"
        if key:
            message += f": {key}"
        super().__init__(message=message, code="email_template_not_found", status_code=404)


class EmailTemplateKeyInvalid(CmsError):
    """Некорректный ключ email шаблона."""

    def __init__(self):
        super().__init__(message="Некорректный ключ email шаблона. Допустимы только буквы, цифры и подчеркивания", code="email_template_key_invalid", status_code=400)


class EmailTemplateKeyAlreadyExists(CmsError):
    """Ключ email шаблона уже существует."""

    def __init__(self, key: str):
        self.key = key
        super().__init__(message=f"Email шаблон с ключом '{key}' уже существует", code="email_template_key_exists", status_code=400)


class FeatureFlagNotFound(CmsError):
    """Feature flag не найден."""

    def __init__(self, key: str | None = None):
        self.key = key
        message = "Feature flag не найден"
        if key:
            message += f": {key}"
        super().__init__(message=message, code="feature_flag_not_found", status_code=404)


class FeatureFlagKeyAlreadyExists(CmsError):
    """Ключ feature flag уже существует."""

    def __init__(self, key: str):
        self.key = key
        super().__init__(message=f"Feature flag с ключом '{key}' уже существует", code="feature_flag_key_exists", status_code=400)


class SeoNotFound(CmsError):
    """SEO данные не найдены."""

    def __init__(self, page_slug: str | None = None):
        self.page_slug = page_slug
        message = "SEO данные не найдены"
        if page_slug:
            message += f": {page_slug}"
        super().__init__(message=message, code="seo_not_found", status_code=404)


__all__ = [
    "CmsError",
    "EmailTemplateKeyAlreadyExists",
    "EmailTemplateKeyInvalid",
    "EmailTemplateNotFound",
    "FaqNotFound",
    "FeatureFlagKeyAlreadyExists",
    "FeatureFlagNotFound",
    "PageBlockNotFound",
    "PageBlockTypeInvalid",
    "PageNotFound",
    "PageSlugAlreadyExists",
    "PageSlugInvalid",
    "SeoNotFound",
]
