from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.product.domain.aggregates.product import (
    ProductAggregate,
    ProductAttributeAggregate,
    ProductImageAggregate,
)
from src.catalog.product.domain.exceptions import ProductNotFound
from src.catalog.product.domain.repository.product import ProductRepository
from src.catalog.product.infrastructure.models.product import Product
from src.catalog.product.infrastructure.models.product_attribute import ProductAttribute
from src.catalog.product.infrastructure.models.product_attribute_value import ProductAttributeValue
from src.catalog.product.infrastructure.models.product_image import ProductImage


class SqlAlchemyProductRepository(ProductRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, product_id: int) -> Optional[ProductAggregate]:
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

        return self._to_aggregate(model)

    async def get_by_name(self, name: str) -> Optional[ProductAggregate]:
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

        return self._to_aggregate(model)

    async def create(self, aggregate: ProductAggregate) -> ProductAggregate:
        model = Product(
            name=aggregate.name,
            description=aggregate.description,
            price=aggregate.price,
            category_id=aggregate.category_id,
            supplier_id=aggregate.supplier_id,
            product_type_id=aggregate.product_type_id,
        )
        self.db.add(model)
        await self.db.flush()

        for image in aggregate.images:
            self.db.add(
                ProductImage(
                    product_id=model.id,
                    image_url=image.object_key,
                    is_main=image.is_main,
                )
            )

        await self._replace_attributes(model.id, aggregate.attributes)
        await self.db.flush()

        aggregate._set_id(model.id)
        return aggregate

    async def update(self, aggregate: ProductAggregate) -> ProductAggregate:
        model = await self.db.get(Product, aggregate.id)

        if not model:
            raise ProductNotFound()

        model.name = aggregate.name
        model.description = aggregate.description
        model.price = aggregate.price
        model.category_id = aggregate.category_id
        model.supplier_id = aggregate.supplier_id
        model.product_type_id = aggregate.product_type_id

        if aggregate.images is not None:
            result = await self.db.execute(
                select(ProductImage).where(ProductImage.product_id == aggregate.id)
            )
            for image_model in result.scalars().all():
                await self.db.delete(image_model)

            for image in aggregate.images:
                self.db.add(
                    ProductImage(
                        product_id=aggregate.id,
                        image_url=image.object_key,
                        is_main=image.is_main,
                    )
                )

        await self._replace_attributes(aggregate.id, aggregate.attributes)

        await self.db.flush()
        return aggregate

    async def delete(self, product_id: int) -> bool:
        model = await self.db.get(Product, product_id)

        if not model:
            return False

        await self.db.delete(model)
        return True

    async def get_related_by_filterable_attributes(
        self,
        product_id: int,
        category_id: Optional[int],
    ) -> list[ProductAggregate]:
        if category_id is None:
            base = await self.get(product_id)
            return [base] if base else []

        filterable_names_stmt = (
            select(ProductAttribute.name)
            .join(ProductAttributeValue, ProductAttribute.id == ProductAttributeValue.attribute_id)
            .where(
                ProductAttributeValue.product_id == product_id,
                ProductAttribute.is_filterable.is_(True),
            )
        )
        filterable_names_result = await self.db.execute(filterable_names_stmt)
        filterable_names = [row[0] for row in filterable_names_result.all()]

        stmt = (
            select(Product)
            .options(
                selectinload(Product.images),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
            )
            .where(Product.category_id == category_id)
            .order_by(Product.id)
        )

        if filterable_names:
            stmt = stmt.where(
                Product.attributes.any(
                    ProductAttributeValue.attribute.has(
                        ProductAttribute.name.in_(filterable_names),
                    )
                )
            )

        result = await self.db.execute(stmt)
        return [self._to_aggregate(model) for model in result.scalars().all()]

    async def _replace_attributes(
        self,
        product_id: int,
        attributes: list[ProductAttributeAggregate],
    ):
        existing_values = await self.db.execute(
            select(ProductAttributeValue).where(ProductAttributeValue.product_id == product_id)
        )
        for attr_value in existing_values.scalars().all():
            await self.db.delete(attr_value)

        for attribute in attributes:
            attribute_name = attribute.name.strip()
            stmt = select(ProductAttribute).where(ProductAttribute.name == attribute_name)
            attr_result = await self.db.execute(stmt)
            attr_model = attr_result.scalar_one_or_none()

            if not attr_model:
                attr_model = ProductAttribute(
                    name=attribute_name,
                    is_filterable=attribute.is_filterable,
                )
                self.db.add(attr_model)
                await self.db.flush()
            else:
                attr_model.is_filterable = attribute.is_filterable

            self.db.add(
                ProductAttributeValue(
                    product_id=product_id,
                    attribute_id=attr_model.id,
                    value=attribute.value,
                )
            )

    @staticmethod
    def _to_aggregate(model: Product) -> ProductAggregate:
        return ProductAggregate(
            product_id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            category_id=model.category_id,
            supplier_id=model.supplier_id,
            product_type_id=model.product_type_id,
            images=[
                ProductImageAggregate(
                    object_key=image.image_url,
                    is_main=image.is_main,
                )
                for image in model.images
            ],
            attributes=[
                ProductAttributeAggregate(
                    name=attribute_value.attribute.name,
                    value=attribute_value.value,
                    is_filterable=attribute_value.attribute.is_filterable,
                )
                for attribute_value in model.attributes
            ],
        )
