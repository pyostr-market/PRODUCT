from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class Supplier(TimestampMixin, Base):
    __tablename__ = "suppliers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)
    contact_email = Column(String(150), nullable=True)
    phone = Column(String(50), nullable=True)

    products = relationship(
        "Product",
        back_populates="supplier",
        cascade="all, delete",
    )
