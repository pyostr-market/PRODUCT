from sqlalchemy import BigInteger, Column, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin

class CategoryPricingPolicy(TimestampMixin, Base):
    __tablename__ = "category_pricing_policies"

    id = Column(BigInteger, primary_key=True)

    category_id = Column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    # Наценка
    markup_fixed = Column(Numeric(12,2), nullable=True)
    markup_percent = Column(Numeric(5,2), nullable=True)

    # Комиссия маркетплейса
    commission_percent = Column(Numeric(5,2), nullable=True)

    # Скидка категории (если есть)
    discount_percent = Column(Numeric(5,2), nullable=True)

    # НДС
    tax_rate = Column(Numeric(5,2), nullable=False)

    category = relationship(
        "Category",
        back_populates="category_pricing_policies",
    )