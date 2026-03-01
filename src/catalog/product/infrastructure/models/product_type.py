from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductType(TimestampMixin, Base):
    __tablename__ = "product_types"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    name = Column(String(100), nullable=False, unique=True)
    parent_id = Column(
        BigInteger,
        ForeignKey("product_types.id", ondelete="SET NULL"),
        nullable=True,
    )

    products = relationship(
        "Product",
        back_populates="product_type",
        cascade="all, delete",
    )

    parent = relationship(
        "ProductType",
        remote_side=[id],
        back_populates="children",
    )
    children = relationship(
        "ProductType",
        back_populates="parent",
        cascade="all, delete",
    )
