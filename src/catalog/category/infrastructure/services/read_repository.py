from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.category.application.dto.category import (
    CategoryImageReadDTO,
    CategoryReadDTO,
)
from src.catalog.category.domain.aggregates.category import CategoryAggregate
from src.catalog.category.infrastructure.models.categories import Category
from src.catalog.category.infrastructure.models.category_image import CategoryImage
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.catalog.manufacturer.infrastructure.models.manufacturer import Manufacturer
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.infrastructure.models.product_type import ProductType
from src.core.services.images.storage import S3ImageStorageService


class CategoryReadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.image_storage = S3ImageStorageService.from_settings()

    def _to_read_dto(self, model: Category) -> CategoryReadDTO:
        parent_dto = None
        if model.parent:
            parent_dto = CategoryAggregate(
                category_id=model.parent.id,
                name=model.parent.name,
                description=model.parent.description,
                parent_id=model.parent.parent_id,
                manufacturer_id=model.parent.manufacturer_id,
                device_type_id=model.parent.device_type_id,
            )

        manufacturer_dto = None
        if model.manufacturer:
            manufacturer_dto = ManufacturerAggregate(
                manufacturer_id=model.manufacturer.id,
                name=model.manufacturer.name,
                description=model.manufacturer.description,
            )

        device_type_dto = None
        if model.device_type:
            device_type_dto = ProductTypeAggregate(
                product_type_id=model.device_type.id,
                name=model.device_type.name,
                parent_id=model.device_type.parent_id,
            )

        image_dto = None
        if model.images:
            img = model.images[0]
            image_dto = CategoryImageReadDTO(
                image_key=img.upload.file_path,
                image_url=self.image_storage.build_public_url(img.upload.file_path),
                upload_id=img.upload_id,
            )

        return CategoryReadDTO(
            id=model.id,
            name=model.name,
            description=model.description,
            image=image_dto,
            parent_id=model.parent_id,
            parent=parent_dto,
            manufacturer=manufacturer_dto,
            device_type=device_type_dto,
        )

    async def get_by_id(self, category_id: int) -> Optional[CategoryReadDTO]:
        stmt = (
            select(Category)
            .options(
                selectinload(Category.images).selectinload(CategoryImage.upload),
                selectinload(Category.parent),
                selectinload(Category.manufacturer),
                selectinload(Category.device_type),
            )
            .where(Category.id == category_id)
        )

        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            return None

        return self._to_read_dto(model)

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[CategoryReadDTO], int]:

        stmt = select(Category).options(
            selectinload(Category.images).selectinload(CategoryImage.upload),
            selectinload(Category.parent),
            selectinload(Category.manufacturer),
            selectinload(Category.device_type),
        )

        count_stmt = select(func.count()).select_from(Category)

        if name:
            stmt = stmt.where(Category.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(Category.name.ilike(f"%{name}%"))

        stmt = stmt.order_by(Category.id).limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [self._to_read_dto(model) for model in result.scalars().all()]
        total = count_result.scalar() or 0
        return items, total

    async def get_tree(self) -> List[CategoryReadDTO]:
        """
        Получить все категории в виде плоского списка с данными для построения дерева.
        Загружает все категории с изображениями, родителями и производителями.
        """
        stmt = select(Category).options(
            selectinload(Category.images).selectinload(CategoryImage.upload),
            selectinload(Category.parent),
            selectinload(Category.manufacturer),
            selectinload(Category.device_type),
            selectinload(Category.children),
        ).order_by(Category.id)

        result = await self.db.execute(stmt)
        categories = result.scalars().all()

        return [self._to_read_dto(model) for model in categories]
