from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class Manufacturer(TimestampMixin, Base):
    __tablename__ = "manufacturers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(String(255), nullable=True)

    categories = relationship(
        "Category",
        back_populates="manufacturer",
        cascade="all, delete",
    )