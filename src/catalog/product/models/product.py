from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_category_id", "category_id"),
        Index("ix_products_supplier_id", "supplier_id"),
        Index("ix_products_product_type_id", "product_type_id"),
    )
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=False)

    # 📂 Категория
    category_id = Column(
        BigInteger,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )

    category = relationship(
        "Category",
        back_populates="products",
    )

    # 🚚 Поставщик
    supplier_id = Column(
        BigInteger,
        ForeignKey("suppliers.id", ondelete="SET NULL"),
        nullable=True,
    )

    supplier = relationship(
        "Supplier",
        back_populates="products",
    )

    # 🏷 Тип продукта
    product_type_id = Column(
        BigInteger,
        ForeignKey("product_types.id", ondelete="SET NULL"),
        nullable=True,
    )

    product_type = relationship(
        "ProductType",
        back_populates="products",
    )

    # 🖼 Изображения
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
    )