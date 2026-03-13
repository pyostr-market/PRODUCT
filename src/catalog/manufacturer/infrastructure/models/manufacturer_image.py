from sqlalchemy import BigInteger, Column, ForeignKey, Index, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ManufacturerImage(TimestampMixin, Base):
    __tablename__ = "manufacturer_images"
    __table_args__ = (
        Index("ix_manufacturer_images_manufacturer_id", "manufacturer_id", unique=True),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    manufacturer_id = Column(
        BigInteger,
        ForeignKey("manufacturers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # Только одно изображение на производителя
    )

    # Ссылка на UploadHistory
    upload_id = Column(
        BigInteger,
        ForeignKey("upload_history.id", ondelete="RESTRICT"),
        nullable=False,
    )

    manufacturer = relationship(
        "Manufacturer",
        back_populates="image",
    )

    upload = relationship(
        "UploadHistory",
        back_populates="manufacturer_images",
    )
