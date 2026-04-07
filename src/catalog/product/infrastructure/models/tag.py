from sqlalchemy import (
    BigInteger,
    Column,
    Index,
    String,
)
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class Tag(TimestampMixin, Base):
    __tablename__ = "tags"
    __table_args__ = (
        Index("ix_tags_name", "name", unique=True),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=True)

    # Связи
    products = relationship(
        "ProductTag",
        back_populates="tag",
        cascade="all, delete-orphan",
    )
