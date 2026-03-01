from sqlalchemy import BigInteger, Boolean, Column, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductAttribute(TimestampMixin, Base):
    __tablename__ = "product_attributes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    is_filterable = Column(Boolean, nullable=False, default=False)

    values = relationship(
        "ProductAttributeValue",
        back_populates="attribute",
        cascade="all, delete",
    )
