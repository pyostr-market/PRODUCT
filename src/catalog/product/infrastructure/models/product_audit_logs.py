from sqlalchemy import JSON, BigInteger, Column, ForeignKey, String

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductAuditLog(TimestampMixin, Base):
    __tablename__ = "product_audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    action = Column(String(50), nullable=False)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    user_id = Column(BigInteger, nullable=False)
