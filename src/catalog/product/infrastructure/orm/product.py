from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.category.domain.aggregates.category import CategoryAggregate
from src.catalog.category.infrastructure.models.categories import Category
from src.catalog.manufacturer.domain.aggregates.manufacturer import ManufacturerAggregate
from src.catalog.product.domain.aggregates.product import (
    ProductAggregate,
    ProductAttributeAggregate,
    ProductImageAggregate,
)
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.domain.exceptions import ProductNotFound
from src.catalog.product.domain.repository.product import ProductRepository
from src.catalog.product.infrastructure.models.product import Product
from src.catalog.product.infrastructure.models.product_attribute import ProductAttribute
from src.catalog.product.infrastructure.models.product_attribute_value import ProductAttributeValue
from src.catalog.product.infrastructure.models.product_image import ProductImage
from src.catalog.product.infrastructure.models.product_type import ProductType
from src.catalog.suppliers.domain.aggregates.supplier import SupplierAggregate
from src.catalog.suppliers.infrastructure.models.supplier import Supplier


class SqlAlchemyProductRepository(ProductRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, product_id: int) -> Optional[ProductAggregate]:
        stmt = (
            select(Product)
            .options(
                selectinload(Product.images).selectinload(ProductImage.upload),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
                selectinload(Product.category),
                selectinload(Product.supplier),
                selectinload(Product.product_type),
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
                selectinload(Product.images).selectinload(ProductImage.upload),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
                selectinload(Product.category),
                selectinload(Product.supplier),
                selectinload(Product.product_type),
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
            image_model = ProductImage(
                product_id=model.id,
                upload_id=image.upload_id,
                is_main=image.is_main,
                ordering=image.ordering,
            )
            self.db.add(image_model)

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
            await self._update_images(model.id, aggregate.images)

        await self._replace_attributes(aggregate.id, aggregate.attributes)

        await self.db.flush()
        return aggregate

    async def _update_images(
        self,
        product_id: int,
        images: list[ProductImageAggregate],
    ):
        """
        Частичное обновление изображений товара.

        Изображения определяются по upload_id:
        - upload_id существует в БД - обновить/сохранить запись
        - upload_id не существует в БД - создать новую запись

        При удалении записи из product_images файл в S3 НЕ удаляется.
        """
        existing_upload_ids: set[int] = set()
        new_images_indices: list[int] = []
        # upload_id -> (is_main, ordering | None)
        existing_image_updates: dict[int, tuple[bool, Optional[int]]] = {}

        for idx, image in enumerate(images):
            if image.upload_id in existing_upload_ids:
                # Дубликат upload_id - пропускаем
                continue

            # Проверяем, существует ли уже запись с этим upload_id для этого товара
            stmt = select(ProductImage).where(
                ProductImage.product_id == product_id,
                ProductImage.upload_id == image.upload_id,
            )
            result = await self.db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                existing_upload_ids.add(image.upload_id)
                existing_image_updates[image.upload_id] = (
                    image.is_main,
                    image.ordering if image.ordering is not None else None
                )
            else:
                new_images_indices.append(idx)

        result = await self.db.execute(
            select(ProductImage).where(ProductImage.product_id == product_id)
        )
        all_existing_images = list(result.scalars().all())

        for image_model in all_existing_images:
            if image_model.upload_id not in existing_upload_ids:
                # Удаляем только запись из БД, файл в S3 остаётся
                await self.db.delete(image_model)
            elif image_model.upload_id in existing_image_updates:
                is_main, ordering_value = existing_image_updates[image_model.upload_id]
                image_model.is_main = is_main
                if ordering_value is not None:
                    image_model.ordering = ordering_value

        new_image_models: list[ProductImage] = []
        for idx in new_images_indices:
            image = images[idx]
            image_model = ProductImage(
                product_id=product_id,
                upload_id=image.upload_id,
                is_main=image.is_main,
                ordering=image.ordering if image.ordering is not None else 0,
            )
            self.db.add(image_model)
            new_image_models.append(image_model)

        await self.db.flush()

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
                selectinload(Product.images).selectinload(ProductImage.upload),
                selectinload(Product.attributes).selectinload(ProductAttributeValue.attribute),
                selectinload(Product.category),
                selectinload(Product.supplier),
                selectinload(Product.product_type),
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
        category = None
        if model.category:
            category = CategoryAggregate(
                category_id=model.category.id,
                name=model.category.name,
                description=model.category.description,
                parent_id=model.category.parent_id,
                manufacturer_id=model.category.manufacturer_id,
            )

        supplier = None
        if model.supplier:
            supplier = SupplierAggregate(
                supplier_id=model.supplier.id,
                name=model.supplier.name,
                contact_email=model.supplier.contact_email,
                phone=model.supplier.phone,
            )

        product_type = None
        if model.product_type:
            product_type = ProductTypeAggregate(
                name=model.product_type.name,
                parent_id=model.product_type.parent_id,
                product_type_id=model.product_type.id,
            )

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
                    upload_id=image.upload_id,
                    is_main=image.is_main,
                    ordering=image.ordering,
                    object_key=image.upload.file_path if image.upload else None,
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
            category=category,
            supplier=supplier,
            product_type=product_type,
        )
