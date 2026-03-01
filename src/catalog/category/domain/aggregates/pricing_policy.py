from decimal import Decimal
from typing import Optional

from src.catalog.category.domain.exceptions import CategoryPricingPolicyInvalidRateValue


class CategoryPricingPolicyAggregate:
    """
    Агрегат политики ценообразования категории.
    
    Содержит правила расчёта конечной цены товара в категории:
    - Наценка (фиксированная и процентная)
    - Комиссия маркетплейса
    - Скидка категории
    - НДС
    """

    def __init__(
        self,
        category_id: int,
        markup_fixed: Optional[Decimal] = None,
        markup_percent: Optional[Decimal] = None,
        commission_percent: Optional[Decimal] = None,
        discount_percent: Optional[Decimal] = None,
        tax_rate: Decimal = Decimal("0.00"),
        pricing_policy_id: Optional[int] = None,
    ):
        self._id = pricing_policy_id
        self._category_id = category_id
        
        # Валидация и установка значений
        # markup_fixed - фиксированная сумма, может быть любой
        self._markup_fixed = markup_fixed
        # Остальные поля - проценты, должны быть 0-100
        self._markup_percent = self._validate_percentage_value(markup_percent, "markup_percent")
        self._commission_percent = self._validate_percentage_value(commission_percent, "commission_percent")
        self._discount_percent = self._validate_percentage_value(discount_percent, "discount_percent")
        self._tax_rate = self._validate_tax_rate(tax_rate)

    @staticmethod
    def _validate_percentage_value(value: Optional[Decimal], field_name: str) -> Optional[Decimal]:
        """Валидация процентных значений (от 0 до 100)."""
        if value is None:
            return None
        
        if value < Decimal("0") or value > Decimal("100"):
            raise CategoryPricingPolicyInvalidRateValue(
                details={
                    "field": field_name,
                    "value": str(value),
                    "reason": "Value must be between 0 and 100",
                }
            )
        
        return value

    @staticmethod
    def _validate_tax_rate(value: Decimal) -> Decimal:
        """Валидация ставки НДС (от 0 до 100)."""
        if value < Decimal("0") or value > Decimal("100"):
            raise CategoryPricingPolicyInvalidRateValue(
                details={
                    "field": "tax_rate",
                    "value": str(value),
                    "reason": "Tax rate must be between 0 and 100",
                }
            )
        
        return value

    # -----------------------------
    # Identity
    # -----------------------------

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def category_id(self) -> int:
        return self._category_id

    # -----------------------------
    # State
    # -----------------------------

    @property
    def markup_fixed(self) -> Optional[Decimal]:
        return self._markup_fixed

    @property
    def markup_percent(self) -> Optional[Decimal]:
        return self._markup_percent

    @property
    def commission_percent(self) -> Optional[Decimal]:
        return self._commission_percent

    @property
    def discount_percent(self) -> Optional[Decimal]:
        return self._discount_percent

    @property
    def tax_rate(self) -> Decimal:
        return self._tax_rate

    # -----------------------------
    # Behavior
    # -----------------------------

    def update_markup_fixed(self, markup_fixed: Optional[Decimal]):
        # markup_fixed - фиксированная сумма, может быть любой
        self._markup_fixed = markup_fixed

    def update_markup_percent(self, markup_percent: Optional[Decimal]):
        self._markup_percent = self._validate_percentage_value(markup_percent, "markup_percent")

    def update_commission_percent(self, commission_percent: Optional[Decimal]):
        self._commission_percent = self._validate_percentage_value(commission_percent, "commission_percent")

    def update_discount_percent(self, discount_percent: Optional[Decimal]):
        self._discount_percent = self._validate_percentage_value(discount_percent, "discount_percent")

    def update_tax_rate(self, tax_rate: Decimal):
        self._tax_rate = self._validate_tax_rate(tax_rate)

    def update(
        self,
        markup_fixed: Optional[Decimal] = None,
        markup_percent: Optional[Decimal] = None,
        commission_percent: Optional[Decimal] = None,
        discount_percent: Optional[Decimal] = None,
        tax_rate: Optional[Decimal] = None,
    ):
        if markup_fixed is not None:
            self.update_markup_fixed(markup_fixed)
        if markup_percent is not None:
            self.update_markup_percent(markup_percent)
        if commission_percent is not None:
            self.update_commission_percent(commission_percent)
        if discount_percent is not None:
            self.update_discount_percent(discount_percent)
        if tax_rate is not None:
            self.update_tax_rate(tax_rate)

    # -----------------------------
    # Internal
    # -----------------------------

    def _set_id(self, pricing_policy_id: int):
        self._id = pricing_policy_id
