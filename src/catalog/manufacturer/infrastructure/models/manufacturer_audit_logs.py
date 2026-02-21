from sqlalchemy import JSON, BigInteger, Column, ForeignKey, String

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ManufacturerAuditLog(TimestampMixin, Base):
    __tablename__ = "manufacturer_audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    manufacturer_id = Column(
        BigInteger,
        ForeignKey("manufacturers.id", ondelete="CASCADE"),
        nullable=False,
    )

    action = Column(String(50), nullable=False)

    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)

    user_id = Column(BigInteger, nullable=False)
    fio = Column(String(255), nullable=True)