from sqlalchemy import BigInteger, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ProductRelationAuditLog(TimestampMixin, Base):
    __tablename__ = "product_relation_audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    relation_id = Column(BigInteger, nullable=False)
    action = Column(String(50), nullable=False)  # create, update, delete
    old_data = Column(Text, nullable=True)  # JSON
    new_data = Column(Text, nullable=True)  # JSON
    user_id = Column(BigInteger, nullable=False)
    fio = Column(String(255), nullable=True)
