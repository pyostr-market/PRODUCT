from sqlalchemy import BigInteger, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    parent_id = Column(
        BigInteger,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    manufacturer_id = Column(
        BigInteger,
        ForeignKey("manufacturers.id", ondelete="SET NULL"),
        nullable=True,
    )

    parent = relationship(
        "Category",
        remote_side=[id],
        back_populates="children",
    )
    children = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete",
    )

    manufacturer = relationship(
        "Manufacturer",
        back_populates="categories",
    )

    images = relationship(
        "CategoryImage",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    products = relationship(
        "Product",
        back_populates="category",
    )

    category_pricing_policy = relationship(
        "CategoryPricingPolicy",
        back_populates="category",
        uselist=False,
        cascade="all, delete-orphan",
    )
