"""add fio to audit tables

Revision ID: 199fe24ccdd8
Revises: af7b8ae1e6a8
Create Date: 2026-02-22 00:32:25.468035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '199fe24ccdd8'
down_revision: Union[str, Sequence[str], None] = 'af7b8ae1e6a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('product_audit_logs', sa.Column('fio', sa.String(length=255), nullable=True))
    op.add_column('product_type_audit_logs', sa.Column('fio', sa.String(length=255), nullable=True))
    op.add_column('product_attribute_audit_logs', sa.Column('fio', sa.String(length=255), nullable=True))
    op.add_column('category_audit_logs', sa.Column('fio', sa.String(length=255), nullable=True))
    op.add_column('manufacturer_audit_logs', sa.Column('fio', sa.String(length=255), nullable=True))
    op.add_column('supplier_audit_logs', sa.Column('fio', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('supplier_audit_logs', 'fio')
    op.drop_column('manufacturer_audit_logs', 'fio')
    op.drop_column('category_audit_logs', 'fio')
    op.drop_column('product_attribute_audit_logs', 'fio')
    op.drop_column('product_type_audit_logs', 'fio')
    op.drop_column('product_audit_logs', 'fio')
