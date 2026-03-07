from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, Text, ARRAY
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class CmsSeo(TimestampMixin, Base):
    """Модель SEO данных."""

    __tablename__ = "cms_seo"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    page_slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    keywords = Column(ARRAY(String), nullable=True)
    og_image_id = Column(BigInteger, nullable=True)

    # Связи (без FK чтобы SEO можно было создавать независимо от страниц)
    page = relationship(
        "CmsPage",
        primaryjoin="CmsSeo.page_slug == CmsPage.slug",
        foreign_keys=[page_slug],
        uselist=False,
    )
