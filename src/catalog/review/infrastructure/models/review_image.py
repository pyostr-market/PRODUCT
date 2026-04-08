"""SQLAlchemy модель изображения отзыва."""

from sqlalchemy import BigInteger, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ReviewImage(TimestampMixin, Base):
    __tablename__ = "review_images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    review_id = Column(
        BigInteger,
        ForeignKey("reviews.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Ссылка на UploadHistory
    upload_id = Column(
        BigInteger,
        ForeignKey("upload_history.id", ondelete="RESTRICT"),
        nullable=False,
    )

    ordering = Column(Integer, default=0, nullable=False)

    review = relationship(
        "Review",
        back_populates="images",
    )

    upload = relationship(
        "UploadHistory",
        back_populates="review_images",
    )
