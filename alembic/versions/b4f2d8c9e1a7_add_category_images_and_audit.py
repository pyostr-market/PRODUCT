"""add category images and audit

Revision ID: b4f2d8c9e1a7
Revises: 8c5fd2dd4c3e
Create Date: 2026-02-20 23:20:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b4f2d8c9e1a7"
down_revision: Union[str, Sequence[str], None] = "8c5fd2dd4c3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "category_images",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("category_id"),
    )

    op.create_table(
        "category_audit_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.BigInteger(), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_data", sa.JSON(), nullable=True),
        sa.Column("new_data", sa.JSON(), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("category_audit_logs")
    op.drop_table("category_images")
