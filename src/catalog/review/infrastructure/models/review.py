"""SQLAlchemy модель отзыва товара."""

from sqlalchemy import BigInteger, Column, ForeignKey, Numeric, String, Text, Index
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class Review(TimestampMixin, Base):
    __tablename__ = "reviews"
    # __table_args__ = (
    #     Index("ix_reviews_product_id", "product_id"),
    #     Index("ix_reviews_user_id", "user_id"),
    #     Index("ix_reviews_product_user", "product_id", "user_id", unique=True),
    # )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # ID товара
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ID пользователя, оставившего отзыв
    user_id = Column(BigInteger, nullable=False)

    # Имя пользователя (из JWT на момент создания)
    username = Column(String(255), nullable=False)

    # Рейтинг (1-5)
    rating = Column(Numeric(2, 1), nullable=False)

    # Текст отзыва (может быть NULL, если только рейтинг)
    text = Column(Text, nullable=True)

    # Связи
    product = relationship(
        "Product",
        back_populates="reviews",
    )

    images = relationship(
        "ReviewImage",
        back_populates="review",
        cascade="all, delete-orphan",
    )
