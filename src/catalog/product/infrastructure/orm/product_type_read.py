from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.product.application.dto.product_type import ProductTypeImageReadDTO, ProductTypeReadDTO
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.domain.repository.product_type_read import (
    ProductTypeReadRepositoryInterface,
)
from src.catalog.product.infrastructure.models.product_type import ProductType
from src.catalog.product.infrastructure.models.product_type_image import ProductTypeImage
from src.uploads.infrastructure.models.upload_history import UploadHistory


class SqlAlchemyProductTypeReadRepository(ProductTypeReadRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db
        self._image_storage = None

    @property
    def image_storage(self):
        if self._image_storage is None:
            from src.core.services.images.storage import S3ImageStorageService
            self._image_storage = S3ImageStorageService.from_settings()
        return self._image_storage

    def _build_image_url(self, file_path: str) -> str:
        """Построить публичный URL для изображения."""
        try:
            return self.image_storage.build_public_url(file_path)
        except Exception:
            return ""

    def _to_read_dto(self, model: ProductType) -> ProductTypeReadDTO:
        parent_dto = None
        if model.parent:
            parent_dto = ProductTypeAggregate(
                product_type_id=model.parent.id,
                name=model.parent.name,
                parent_id=model.parent.parent_id,
            )

        image_dto = None
        if model.image and model.image.upload:
            image_dto = ProductTypeImageReadDTO(
                upload_id=model.image.upload_id,
                image_url=self._build_image_url(model.image.upload.file_path),
            )

        return ProductTypeReadDTO(
            id=model.id,
            name=model.name,
            parent_id=model.parent_id,
            parent=parent_dto,
            children=[],
            image=image_dto,
        )

    async def get_by_id(self, product_type_id: int) -> Optional[ProductTypeReadDTO]:
        stmt = select(ProductType).options(
            selectinload(ProductType.parent),
            selectinload(ProductType.image)
            .selectinload(ProductTypeImage.upload),
        ).where(ProductType.id == product_type_id)

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
    ) -> Tuple[List[ProductTypeReadDTO], int]:

        stmt = select(ProductType).options(
            selectinload(ProductType.parent),
            selectinload(ProductType.image)
            .selectinload(ProductTypeImage.upload),
        )

        count_stmt = select(func.count()).select_from(ProductType)

        if name:
            stmt = stmt.where(ProductType.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(
                ProductType.name.ilike(f"%{name}%")
            )

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        items = [self._to_read_dto(model) for model in result.scalars().all()]
        total = count_result.scalar() or 0
        return items, total

    async def get_tree(self) -> List[ProductTypeReadDTO]:
        """
        Получить все типы продуктов в виде плоского списка с данными для построения дерева.
        Загружает все типы продуктов с родителями.
        """
        stmt = select(ProductType).options(
            selectinload(ProductType.parent),
            selectinload(ProductType.children),
            selectinload(ProductType.image)
            .selectinload(ProductTypeImage.upload),
        ).order_by(ProductType.id)

        result = await self.db.execute(stmt)
        product_types = result.scalars().all()

        return [self._to_read_dto(model) for model in product_types]
