from sqlalchemy import BigInteger, Boolean, Column, Integer, String, Text
from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class CmsFeatureFlag(TimestampMixin, Base):
    """Модель feature flag."""

    __tablename__ = "cms_feature_flags"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    enabled = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)
