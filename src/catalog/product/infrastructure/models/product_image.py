from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductImage(TimestampMixin, Base):
    __tablename__ = "product_images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Ссылка на UploadHistory
    upload_id = Column(
        BigInteger,
        ForeignKey("upload_history.id", ondelete="RESTRICT"),
        nullable=False,
    )

    is_main = Column(Boolean, default=False)
    ordering = Column(Integer, default=0, nullable=False)

    product = relationship(
        "Product",
        back_populates="images",
    )

    upload = relationship(
        "UploadHistory",
        back_populates="product_images",
    )
