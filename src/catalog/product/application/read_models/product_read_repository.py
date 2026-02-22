from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.product.application.dto.product import (
    ProductAttributeReadDTO,
    ProductImageReadDTO,
    ProductReadDTO,
)
from src.catalog.product.infrastructure.models.product import Product
from src.catalog.product.infrastructure.models.product_attribute import ProductAttribute
from src.catalog.product.infrastructure.models.product_attribute_value import ProductAttributeValue


class ProductReadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    def _to_read_dto(self, model: Product) -> ProductReadDTO:
        return ProductReadDTO(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            category_id=model.category_id,
            supplier_id=model.supplier_id,
            product_type_id=model.product_type_id,
            images=[
                ProductImageReadDTO(
                    image_id=image.id,
                    image_key=image.image_url,
                    is_main=image.is_main,
                    ordering=image.ordering,
                )
                for image in model.images
            ],
            attributes=[
                ProductAttributeReadDTO(
                    id=attribute_value.attribute.id,
                    name=attribute_value.attribute.name,
                    value=attribute_value.value,
                    is_filterable=attribute_value.attribute.is_filterable,
                )
                for attribute_value in model.attributes
            ],
        )

    async def get_by_id(self, product_id: int) -> Optional[ProductReadDTO]:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
            )
            .where(Product.id == product_id)
        )
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def get_by_name(self, name: str) -> Optional[ProductReadDTO]:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
            )
            .where(Product.name == name)
        )

        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_read_dto(model)

    async def filter(
        self,
        name: Optional[str],
        category_id: Optional[int],
        product_type_id: Optional[int],
        limit: int,
        offset: int,
        attributes: Optional[dict[str, str]] = None,
    ) -> Tuple[List[ProductReadDTO], int]:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
            )
        )
        count_stmt = select(func.count()).select_from(Product)

        if name:
            stmt = stmt.where(Product.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(Product.name.ilike(f"%{name}%"))

        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
            count_stmt = count_stmt.where(Product.category_id == category_id)

        if product_type_id is not None:
            stmt = stmt.where(Product.product_type_id == product_type_id)
            count_stmt = count_stmt.where(Product.product_type_id == product_type_id)

        # Фильтрация по атрибутам
        if attributes:
            for attr_name, attr_value in attributes.items():
                attr_alias = selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute)
                stmt = stmt.where(
                    Product.attributes.any(
                        ProductAttributeValue.attribute.has(
                            ProductAttribute.name == attr_name
                        ),
                        ProductAttributeValue.value == attr_value,
                    )
                )
                count_stmt = count_stmt.where(
                    Product.attributes.any(
                        ProductAttributeValue.attribute.has(
                            ProductAttribute.name == attr_name
                        ),
                        ProductAttributeValue.value == attr_value,
                    )
                )

        stmt = stmt.order_by(Product.id).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [self._to_read_dto(model) for model in result.scalars().all()]
        total = count_result.scalar() or 0

        return items, total
