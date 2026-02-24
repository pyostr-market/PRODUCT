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
from src.catalog.manufacturer.domain.aggregates.manufacturer import ManufacturerAggregate
from src.catalog.manufacturer.infrastructure.models.manufacturer import Manufacturer
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
            )

        manufacturer_dto = None
        if model.manufacturer:
            manufacturer_dto = ManufacturerAggregate(
                manufacturer_id=model.manufacturer.id,
                name=model.manufacturer.name,
                description=model.manufacturer.description,
            )

        return CategoryReadDTO(
            id=model.id,
            name=model.name,
            description=model.description,
            images=[
                CategoryImageReadDTO(
                    ordering=image.ordering,
                    image_key=image.upload.file_path,
                    image_url=self.image_storage.build_public_url(image.upload.file_path),
                    upload_id=image.upload_id,
                )
                for image in sorted(model.images, key=lambda i: i.ordering)
            ],
            parent=parent_dto,
            manufacturer=manufacturer_dto,
        )

    async def get_by_id(self, category_id: int) -> Optional[CategoryReadDTO]:
        stmt = (
            select(Category)
            .options(
                selectinload(Category.images).selectinload(CategoryImage.upload),
                selectinload(Category.parent),
                selectinload(Category.manufacturer),
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
