from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, String
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

    image_url = Column(String(500), nullable=False)
    is_main = Column(Boolean, default=False)

    product = relationship(
        "Product",
        back_populates="images",
    )