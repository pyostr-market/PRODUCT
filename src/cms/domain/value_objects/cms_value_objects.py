from dataclasses import dataclass
import re


@dataclass(frozen=True)
class PageSlug:
    """Value object для slug страницы."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 2:
            raise ValueError("Slug должен содержать минимум 2 символа")

        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', self.value):
            raise ValueError(
                "Slug должен содержать только строчные буквы, цифры и дефисы"
            )


@dataclass(frozen=True)
class PageTitle:
    """Value object для заголовка страницы."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 2:
            raise ValueError("Заголовок должен содержать минимум 2 символа")


@dataclass(frozen=True)
class BlockType:
    """Value object для типа блока страницы."""
    value: str

    VALID_TYPES = {
        'carousel',
        'banner',
        'text',
        'image_text',
        'hero',
        'cta',
        'faq',
        'info',
    }

    def __post_init__(self):
        if self.value not in self.VALID_TYPES:
            raise ValueError(
                f"Некорректный тип блока. Допустимые значения: {self.VALID_TYPES}"
            )


@dataclass(frozen=True)
class FaqCategory:
    """Value object для категории FAQ."""
    value: str | None

    def __post_init__(self):
        if self.value and len(self.value.strip()) < 2:
            raise ValueError("Категория должна содержать минимум 2 символа")


@dataclass(frozen=True)
class EmailTemplateKey:
    """Value object для ключа email шаблона."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 2:
            raise ValueError("Ключ шаблона должен содержать минимум 2 символа")

        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', self.value):
            raise ValueError(
                "Ключ шаблона должен начинаться с буквы и содержать только буквы, цифры и подчеркивания"
            )


@dataclass(frozen=True)
class FeatureFlagKey:
    """Value object для ключа feature flag."""
    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 2:
            raise ValueError("Ключ feature flag должен содержать минимум 2 символа")

        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', self.value):
            raise ValueError(
                "Ключ feature flag должен начинаться с буквы и содержать только буквы, цифры и подчеркивания"
            )
