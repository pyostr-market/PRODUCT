"""add_regions

Revision ID: 77fea243383d
Revises: 85a0ea4f50b7
Create Date: 2026-04-08 20:14:53.304389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77fea243383d'
down_revision: Union[str, Sequence[str], None] = '85a0ea4f50b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем таблицу regions
    op.create_table(
        'regions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['regions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # Создаем таблицу region_audit_logs
    op.create_table(
        'region_audit_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('region_id', sa.BigInteger(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('old_data', sa.JSON(), nullable=True),
        sa.Column('new_data', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('fio', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    # Добавляем region_id в таблицу products
    op.add_column('products', sa.Column('region_id', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_products_region_id', 'products', 'regions', ['region_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_products_region_id', 'products', ['region_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем region_id из products
    op.drop_index('ix_products_region_id', table_name='products')
    op.drop_constraint('fk_products_region_id', 'products', type_='foreignkey')
    op.drop_column('products', 'region_id')

    # Удаляем таблицы regions
    op.drop_table('region_audit_logs')
    op.drop_table('regions')
