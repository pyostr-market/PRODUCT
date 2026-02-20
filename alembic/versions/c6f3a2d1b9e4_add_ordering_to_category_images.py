"""add ordering to category images

Revision ID: c6f3a2d1b9e4
Revises: b4f2d8c9e1a7
Create Date: 2026-02-20 23:55:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "c6f3a2d1b9e4"
down_revision: Union[str, Sequence[str], None] = "b4f2d8c9e1a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("category_images", sa.Column("ordering", sa.Integer(), server_default="0", nullable=False))

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'category_images_category_id_key'
            ) THEN
                ALTER TABLE category_images DROP CONSTRAINT category_images_category_id_key;
            END IF;
        END $$;
        """
    )

    op.create_index("ix_category_images_category_id_ordering", "category_images", ["category_id", "ordering"])


def downgrade() -> None:
    op.drop_index("ix_category_images_category_id_ordering", table_name="category_images")
    op.create_unique_constraint("category_images_category_id_key", "category_images", ["category_id"])
    op.drop_column("category_images", "ordering")
