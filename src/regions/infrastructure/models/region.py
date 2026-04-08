from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class Region(TimestampMixin, Base):
    __tablename__ = "regions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)

    # Иерархия: родительский регион
    parent_id = Column(
        BigInteger,
        ForeignKey("regions.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Обратная связь для дочерних регионов
    children = relationship(
        "Region",
        back_populates="parent",
        remote_side="Region.id",
        cascade="all, delete",
    )

    # Обратная связь для родительского региона
    parent = relationship(
        "Region",
        back_populates="children",
        remote_side="Region.parent_id",
    )

    # Связь с товарами
    products = relationship(
        "Product",
        back_populates="region",
        cascade="all, delete",
    )
