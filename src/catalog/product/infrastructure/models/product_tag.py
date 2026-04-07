from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductTag(TimestampMixin, Base):
    __tablename__ = "product_tags"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "tag_id",
            name="uq_product_tags_unique",
        ),
        Index("ix_product_tags_product_id", "product_id"),
        Index("ix_product_tags_tag_id", "tag_id"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    tag_id = Column(
        BigInteger,
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Связи
    product = relationship(
        "Product",
        foreign_keys=[product_id],
        back_populates="product_tags",
    )

    tag = relationship(
        "Tag",
        foreign_keys=[tag_id],
        back_populates="products",
    )
