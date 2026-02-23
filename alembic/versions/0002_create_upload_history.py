"""create upload_history and update product_images category_images

Revision ID: 0002
Revises: 495d7f879eef
Create Date: 2026-02-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '495d7f879eef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаём таблицу upload_history
    op.create_table('upload_history',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('folder', sa.String(length=100), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=True),
        sa.Column('original_filename', sa.String(length=255), nullable=True),
        sa.Column('file_size', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_path')
    )
    op.create_index('ix_upload_history_folder', 'upload_history', ['folder'], unique=False)
    op.create_index('ix_upload_history_user_id', 'upload_history', ['user_id'], unique=False)

    # Добавляем upload_id в product_images
    op.add_column('product_images', sa.Column('upload_id', sa.BigInteger(), nullable=True))
    
    # Мигрируем данные из image_url в upload_history и связываем
    # Сначала создаём временную таблицу для миграции данных
    op.execute("""
        INSERT INTO upload_history (file_path, folder, content_type, original_filename, created_at, updated_at)
        SELECT DISTINCT image_url, 'products', 'image/jpeg', image_url, NOW(), NOW()
        FROM product_images
        WHERE image_url IS NOT NULL
    """)
    
    # Обновляем product_images.upload_id
    op.execute("""
        UPDATE product_images pi
        SET upload_id = uh.id
        FROM upload_history uh
        WHERE uh.file_path = pi.image_url
    """)
    
    # Делаем upload_id NOT NULL
    op.alter_column('product_images', 'upload_id', nullable=False)
    
    # Создаём foreign key
    op.create_foreign_key(
        'fk_product_images_upload_id',
        'product_images', 'upload_history',
        ['upload_id'], ['id'],
        ondelete='RESTRICT'
    )
    
    # Удаляем старый столбец image_url
    op.drop_column('product_images', 'image_url')

    # Добавляем upload_id в category_images
    op.add_column('category_images', sa.Column('upload_id', sa.BigInteger(), nullable=True))
    
    # Мигрируем данные из object_key в upload_history
    op.execute("""
        INSERT INTO upload_history (file_path, folder, content_type, original_filename, created_at, updated_at)
        SELECT DISTINCT object_key, 'categories', 'image/jpeg', object_key, NOW(), NOW()
        FROM category_images
        WHERE object_key IS NOT NULL
    """)
    
    # Обновляем category_images.upload_id
    op.execute("""
        UPDATE category_images ci
        SET upload_id = uh.id
        FROM upload_history uh
        WHERE uh.file_path = ci.object_key
    """)
    
    # Делаем upload_id NOT NULL
    op.alter_column('category_images', 'upload_id', nullable=False)
    
    # Создаём foreign key
    op.create_foreign_key(
        'fk_category_images_upload_id',
        'category_images', 'upload_history',
        ['upload_id'], ['id'],
        ondelete='RESTRICT'
    )
    
    # Удаляем старый столбец object_key
    op.drop_column('category_images', 'object_key')


def downgrade() -> None:
    # Возвращаем столбцы
    op.add_column('category_images', sa.Column('object_key', sa.String(500), nullable=True))
    op.add_column('product_images', sa.Column('image_url', sa.String(500), nullable=True))
    
    # Копируем данные обратно
    op.execute("""
        UPDATE category_images ci
        SET object_key = uh.file_path
        FROM upload_history uh
        WHERE uh.id = ci.upload_id
    """)
    
    op.execute("""
        UPDATE product_images pi
        SET image_url = uh.file_path
        FROM upload_history uh
        WHERE uh.id = pi.upload_id
    """)
    
    # Делаем столбцы NOT NULL
    op.alter_column('category_images', 'object_key', nullable=False)
    op.alter_column('product_images', 'image_url', nullable=False)
    
    # Удаляем foreign keys
    op.drop_constraint('fk_category_images_upload_id', 'category_images', type_='foreignkey')
    op.drop_constraint('fk_product_images_upload_id', 'product_images', type_='foreignkey')
    
    # Удаляем upload_id
    op.drop_column('category_images', 'upload_id')
    op.drop_column('product_images', 'upload_id')
    
    # Удаляем таблицу upload_history
    op.drop_index('ix_upload_history_user_id', table_name='upload_history')
    op.drop_index('ix_upload_history_folder', table_name='upload_history')
    op.drop_table('upload_history')
