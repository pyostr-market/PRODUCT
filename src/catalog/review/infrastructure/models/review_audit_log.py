"""SQLAlchemy модель audit лога для отзывов."""

from sqlalchemy import BigInteger, Column, ForeignKey, Index, JSON, String

from src.core.db.database import Base
from src.core.db.mixins import TimestampMixin


class ReviewAuditLog(TimestampMixin, Base):
    __tablename__ = "review_audit_logs"
    __table_args__ = (
        Index("ix_review_audit_logs_review_id", "review_id"),
        Index("ix_review_audit_logs_user_id", "user_id"),
        Index("ix_review_audit_logs_action", "action"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # ID отзыва (nullable — сохраняется после удаления отзыва)
    review_id = Column(
        BigInteger,
        ForeignKey("reviews.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Действие: create, update, delete
    action = Column(String(50), nullable=False)

    # Старые данные (JSON)
    old_data = Column(JSON, nullable=True)

    # Новые данные (JSON)
    new_data = Column(JSON, nullable=True)

    # ID пользователя, выполнившего действие
    user_id = Column(BigInteger, nullable=True)

    # ФИО пользователя
    fio = Column(String(255), nullable=True)
