from sqlalchemy import BigInteger, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class CategoryImage(TimestampMixin, Base):
    __tablename__ = "category_images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(
        BigInteger,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Ссылка на UploadHistory
    upload_id = Column(
        BigInteger,
        ForeignKey("upload_history.id", ondelete="RESTRICT"),
        nullable=False,
    )

    ordering = Column(Integer, nullable=False, default=0)

    category = relationship(
        "Category",
        back_populates="images",
    )

    upload = relationship(
        "UploadHistory",
        back_populates="category_images",
    )
