from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.product.infrastructure.models.product_tag import ProductTag


class AddProductTagCommand:
    """Команда для добавления тега к товару."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, product_id: int, tag_id: int) -> None:
        """Выполнить команду."""
        # Проверяем, что связь не существует
        stmt = select(ProductTag).where(
            ProductTag.product_id == product_id,
            ProductTag.tag_id == tag_id,
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("Этот тег уже добавлен к товару")

        product_tag = ProductTag(
            product_id=product_id,
            tag_id=tag_id,
        )
        self.db.add(product_tag)
        await self.db.flush()


class RemoveProductTagCommand:
    """Команда для удаления тега у товара."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, product_id: int, tag_id: int) -> None:
        """Выполнить команду."""
        stmt = select(ProductTag).where(
            ProductTag.product_id == product_id,
            ProductTag.tag_id == tag_id,
        )
        result = await self.db.execute(stmt)
        product_tag = result.scalar_one_or_none()
        if not product_tag:
            raise ValueError("Связь тега с товаром не найдена")

        await self.db.delete(product_tag)
        await self.db.flush()
