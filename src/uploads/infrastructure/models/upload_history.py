from sqlalchemy import BigInteger, Column, Index, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class UploadHistory(Base, TimestampMixin):
    __tablename__ = "upload_history"
    __table_args__ = (
        Index("ix_upload_history_user_id", "user_id"),
        Index("ix_upload_history_folder", "folder"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # ID пользователя, загрузившего файл (опционально, т.к. auth в отдельном сервисе)
    user_id = Column(BigInteger, nullable=True)

    # Путь к файлу в S3 (ключ объекта)
    file_path = Column(String(500), nullable=False, unique=True)

    # Папка/категория файла (products, categories, manufacturers, etc.)
    folder = Column(String(100), nullable=False)

    # MIME тип файла
    content_type = Column(String(100), nullable=True)

    # Исходное имя файла
    original_filename = Column(String(255), nullable=True)

    # Размер файла в байтах
    file_size = Column(BigInteger, nullable=True)

    # Связи с продуктами и категориями
    product_images = relationship(
        "ProductImage",
        back_populates="upload",
    )
    category_images = relationship(
        "CategoryImage",
        back_populates="upload",
    )
