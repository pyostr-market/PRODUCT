from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.domain.aggregates.product_type_image import ProductTypeImageAggregate
from src.catalog.product.domain.exceptions import ProductTypeNotFound
from src.catalog.product.domain.repository.product_type import ProductTypeRepository
from src.catalog.product.infrastructure.models.product_type import ProductType
from src.catalog.product.infrastructure.models.product_type_image import ProductTypeImage


class SqlAlchemyProductTypeRepository(ProductTypeRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, product_type_id: int) -> Optional[ProductTypeAggregate]:
        stmt = select(ProductType).options(
            selectinload(ProductType.image)
        ).where(ProductType.id == product_type_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_aggregate(model)

    async def get_with_parent(self, product_type_id: int) -> Optional[ProductTypeAggregate]:
        stmt = select(ProductType).options(
            selectinload(ProductType.parent),
            selectinload(ProductType.image),
        ).where(ProductType.id == product_type_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_aggregate(model)

    async def get_by_name(self, name: str) -> Optional[ProductTypeAggregate]:
        stmt = select(ProductType).options(
            selectinload(ProductType.image)
        ).where(ProductType.name == name)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_aggregate(model)

    async def create(self, aggregate: ProductTypeAggregate) -> ProductTypeAggregate:
        model = ProductType(
            name=aggregate.name,
            parent_id=aggregate.parent_id,
        )
        self.db.add(model)
        await self.db.flush()
        
        # Сохраняем изображение, если есть
        if aggregate.image:
            image_model = ProductTypeImage(
                product_type_id=model.id,
                upload_id=aggregate.image.upload_id,
            )
            self.db.add(image_model)
        
        aggregate._set_id(model.id)
        return aggregate

    async def update(self, aggregate: ProductTypeAggregate) -> ProductTypeAggregate:
        stmt = select(ProductType).options(
            selectinload(ProductType.image)
            .selectinload(ProductTypeImage.upload),
        ).where(ProductType.id == aggregate.id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            raise ProductTypeNotFound()
        
        model.name = aggregate.name
        model.parent_id = aggregate.parent_id
        
        # Обновляем изображение
        if aggregate.image:
            if model.image:
                # Обновляем существующее
                model.image.upload_id = aggregate.image.upload_id
            else:
                # Создаём новое
                image_model = ProductTypeImage(
                    product_type_id=model.id,
                    upload_id=aggregate.image.upload_id,
                )
                self.db.add(image_model)
        elif model.image and not aggregate.image:
            # Удаляем изображение
            await self.db.delete(model.image)
        
        await self.db.flush()
        return aggregate

    async def delete(self, product_type_id: int) -> bool:
        model = await self.db.get(ProductType, product_type_id)
        if not model:
            return False
        await self.db.delete(model)
        return True

    @staticmethod
    def _to_aggregate(model: ProductType) -> ProductTypeAggregate:
        image = None
        if model.image:
            # object_key не загружаем здесь, т.к. это требует дополнительного запроса
            # Для команд это не критично, т.к. они работают только с upload_id
            image = ProductTypeImageAggregate(
                upload_id=model.image.upload_id,
                object_key=None,
            )
        
        aggregate = ProductTypeAggregate(
            product_type_id=model.id,
            name=model.name,
            parent_id=model.parent_id,
        )
        
        # Устанавливаем изображение после создания агрегата
        if image:
            aggregate.set_image(image)
        
        return aggregate
