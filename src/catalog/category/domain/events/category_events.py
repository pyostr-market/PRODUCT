from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from src.catalog.category.domain.events.base import DomainEvent


@dataclass
class CategoryCreatedEvent(DomainEvent):
    """Событие: категория создана."""

    category_id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    manufacturer_id: Optional[int]
    image_ids: list[int]


@dataclass
class CategoryUpdatedEvent(DomainEvent):
    """Событие: категория обновлена."""

    category_id: int
    changed_fields: dict[str, Any]


@dataclass
class CategoryDeletedEvent(DomainEvent):
    """Событие: категория удалена."""

    category_id: int


@dataclass
class CategoryNameChangedEvent(DomainEvent):
    """Событие: имя категории изменено."""

    category_id: int
    old_name: str
    new_name: str


@dataclass
class CategoryDescriptionChangedEvent(DomainEvent):
    """Событие: описание категории изменено."""

    category_id: int
    old_description: Optional[str]
    new_description: Optional[str]


@dataclass
class CategoryParentChangedEvent(DomainEvent):
    """Событие: родительская категория изменена."""

    category_id: int
    old_parent_id: Optional[int]
    new_parent_id: Optional[int]


@dataclass
class CategoryManufacturerChangedEvent(DomainEvent):
    """Событие: производитель категории изменен."""

    category_id: int
    old_manufacturer_id: Optional[int]
    new_manufacturer_id: Optional[int]


@dataclass
class CategoryImageAddedEvent(DomainEvent):
    """Событие: изображение добавлено к категории."""

    category_id: int
    upload_id: int
    ordering: int


@dataclass
class CategoryImageRemovedEvent(DomainEvent):
    """Событие: изображение удалено из категории."""

    category_id: int
    upload_id: int


@dataclass
class CategoryImagesReplacedEvent(DomainEvent):
    """Событие: изображения категории заменены."""

    category_id: int
    old_image_ids: list[int]
    new_image_ids: list[int]


@dataclass
class PricingPolicyCreatedEvent(DomainEvent):
    """Событие: политика ценообразования создана."""

    pricing_policy_id: int
    category_id: int
    markup_fixed: Optional[Decimal]
    markup_percent: Optional[Decimal]
    commission_percent: Optional[Decimal]
    discount_percent: Optional[Decimal]
    tax_rate: Decimal


@dataclass
class PricingPolicyUpdatedEvent(DomainEvent):
    """Событие: политика ценообразования обновлена."""

    pricing_policy_id: int
    changed_fields: dict[str, Any]


@dataclass
class PricingPolicyDeletedEvent(DomainEvent):
    """Событие: политика ценообразования удалена."""

    pricing_policy_id: int
    category_id: int


@dataclass
class PricingPolicyMarkupFixedChangedEvent(DomainEvent):
    """Событие: фиксированная наценка изменена."""

    pricing_policy_id: int
    old_markup_fixed: Optional[Decimal]
    new_markup_fixed: Optional[Decimal]


@dataclass
class PricingPolicyMarkupPercentChangedEvent(DomainEvent):
    """Событие: процентная наценка изменена."""

    pricing_policy_id: int
    old_markup_percent: Optional[Decimal]
    new_markup_percent: Optional[Decimal]


@dataclass
class PricingPolicyCommissionChangedEvent(DomainEvent):
    """Событие: комиссия изменена."""

    pricing_policy_id: int
    old_commission_percent: Optional[Decimal]
    new_commission_percent: Optional[Decimal]


@dataclass
class PricingPolicyDiscountChangedEvent(DomainEvent):
    """Событие: скидка изменена."""

    pricing_policy_id: int
    old_discount_percent: Optional[Decimal]
    new_discount_percent: Optional[Decimal]


@dataclass
class PricingPolicyTaxRateChangedEvent(DomainEvent):
    """Событие: ставка НДС изменена."""

    pricing_policy_id: int
    old_tax_rate: Decimal
    new_tax_rate: Decimal
