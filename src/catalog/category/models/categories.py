from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    __table_args__ = (
        Index("ix_categories_parent_id", "parent_id"),
        Index("ix_categories_manufacturer_id", "manufacturer_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)

    parent_id = Column(
        BigInteger,
        ForeignKey("categories.id", ondelete="CASCADE"),
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

    manufacturer_id = Column(
        BigInteger,
        ForeignKey("manufacturers.id", ondelete="SET NULL"),
        nullable=True,
    )

    manufacturer = relationship(
        "Manufacturer",
        back_populates="categories",
    )

    products = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete",
    )

    images = relationship(
        "CategoryImage",
        back_populates="category",
        order_by="CategoryImage.ordering",
        cascade="all, delete-orphan",
    )
