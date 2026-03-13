from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class CmsPage(TimestampMixin, Base):
    """Модель страницы CMS."""

    __tablename__ = "cms_pages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)

    # Связи
    blocks = relationship(
        "CmsPageBlock",
        back_populates="page",
        cascade="all, delete-orphan",
        order_by="CmsPageBlock.order",
    )

    seo = relationship(
        "CmsSeo",
        back_populates="page",
        uselist=False,
        cascade="all, delete-orphan",
        primaryjoin="CmsPage.slug == CmsSeo.page_slug",
        foreign_keys="CmsSeo.page_slug",
    )
