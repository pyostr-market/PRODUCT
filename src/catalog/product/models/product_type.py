from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductType(TimestampMixin, Base):
    __tablename__ = "product_types"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    name = Column(String(100), nullable=False, unique=True)

    products = relationship(
        "Product",
        back_populates="product_type",
        cascade="all, delete",
    )