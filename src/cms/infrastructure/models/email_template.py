from sqlalchemy import JSON, BigInteger, Boolean, Column, Integer, String, Text

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class CmsEmailTemplate(TimestampMixin, Base):
    """Модель email шаблона."""

    __tablename__ = "cms_email_templates"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text, nullable=True)
    variables = Column(JSON, nullable=True, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
