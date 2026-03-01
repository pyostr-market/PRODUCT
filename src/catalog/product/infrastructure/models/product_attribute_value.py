from sqlalchemy import BigInteger, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductAttributeValue(TimestampMixin, Base):
    __tablename__ = "product_attribute_values"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "attribute_id",
            name="uq_product_attribute_value_per_product",
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    attribute_id = Column(
        BigInteger,
        ForeignKey("product_attributes.id", ondelete="CASCADE"),
        nullable=False,
    )
    value = Column(String(255), nullable=False)

    product = relationship(
        "Product",
        back_populates="attributes",
    )
    attribute = relationship(
        "ProductAttribute",
        back_populates="values",
    )
