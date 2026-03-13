from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Text

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class CmsFaq(TimestampMixin, Base):
    """Модель FAQ."""

    __tablename__ = "cms_faq"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
