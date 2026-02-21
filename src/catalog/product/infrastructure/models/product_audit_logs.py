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


class ProductTypeAuditLog(TimestampMixin, Base):
    __tablename__ = "product_type_audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_type_id = Column(
        BigInteger,
        ForeignKey("product_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    action = Column(String(50), nullable=False)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    user_id = Column(BigInteger, nullable=False)


class ProductAttributeAuditLog(TimestampMixin, Base):
    __tablename__ = "product_attribute_audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_attribute_id = Column(
        BigInteger,
        ForeignKey("product_attributes.id", ondelete="CASCADE"),
        nullable=False,
    )
    action = Column(String(50), nullable=False)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    user_id = Column(BigInteger, nullable=False)
