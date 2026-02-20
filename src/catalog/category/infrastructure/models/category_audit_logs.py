from sqlalchemy import BigInteger, Column, String, JSON, ForeignKey

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class CategoryAuditLog(TimestampMixin, Base):
    __tablename__ = "category_audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    category_id = Column(
        BigInteger,
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )

    action = Column(String(50), nullable=False)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    user_id = Column(BigInteger, nullable=False)
