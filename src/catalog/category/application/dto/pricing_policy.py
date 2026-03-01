from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class CategoryPricingPolicyReadDTO:
    id: int
    category_id: int
    markup_fixed: Optional[Decimal]
    markup_percent: Optional[Decimal]
    commission_percent: Optional[Decimal]
    discount_percent: Optional[Decimal]
    tax_rate: Decimal


@dataclass
class CategoryPricingPolicyCreateDTO:
    category_id: int
    markup_fixed: Optional[Decimal] = None
    markup_percent: Optional[Decimal] = None
    commission_percent: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    tax_rate: Decimal = Decimal("0.00")


@dataclass
class CategoryPricingPolicyUpdateDTO:
    markup_fixed: Optional[Decimal] = None
    markup_percent: Optional[Decimal] = None
    commission_percent: Optional[Decimal] = None
    discount_percent: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
