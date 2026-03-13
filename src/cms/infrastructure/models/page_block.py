from sqlalchemy import JSON, BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class CmsPageBlock(TimestampMixin, Base):
    """Модель блока страницы CMS."""

    __tablename__ = "cms_page_blocks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    page_id = Column(
        BigInteger,
        ForeignKey("cms_pages.id", ondelete="CASCADE"),
        nullable=False,
    )
    block_type = Column(String(50), nullable=False)
    order = Column(Integer, nullable=False, default=0)
    data = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, default=True, nullable=False)

    # Связи
    page = relationship(
        "CmsPage",
        back_populates="blocks",
    )
