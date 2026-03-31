from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductRelation(TimestampMixin, Base):
    __tablename__ = "product_relations"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "related_product_id",
            "relation_type",
            name="uq_product_relations_unique",
        ),
        Index("ix_product_relations_product_id", "product_id"),
        Index("ix_product_relations_related_product_id", "related_product_id"),
        Index("ix_product_relations_relation_type", "relation_type"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    related_product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    relation_type = Column(String(50), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)

    # Связи
    product = relationship(
        "Product",
        foreign_keys=[product_id],
        back_populates="relations",
    )

    related_product = relationship(
        "Product",
        foreign_keys=[related_product_id],
    )
