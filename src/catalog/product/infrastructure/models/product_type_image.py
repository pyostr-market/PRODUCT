from sqlalchemy import BigInteger, Column, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductTypeImage(TimestampMixin, Base):
    __tablename__ = "product_type_images"
    __table_args__ = (
        Index("ix_product_type_images_product_type_id", "product_type_id", unique=True),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    product_type_id = Column(
        BigInteger,
        ForeignKey("product_types.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Только одно изображение на тип продукта
    )

    # Ссылка на UploadHistory
    upload_id = Column(
        BigInteger,
        ForeignKey("upload_history.id", ondelete="RESTRICT"),
        nullable=False,
    )

    product_type = relationship(
        "ProductType",
        back_populates="image",
    )

    upload = relationship(
        "UploadHistory",
        back_populates="product_type_images",
    )
