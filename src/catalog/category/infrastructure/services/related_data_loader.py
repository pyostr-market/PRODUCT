from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.catalog.category.domain.aggregates.category import CategoryAggregate
from src.catalog.category.domain.repository.category import CategoryRepository
from src.catalog.manufacturer.domain.aggregates.manufacturer import (
    ManufacturerAggregate,
)
from src.catalog.manufacturer.infrastructure.models.manufacturer import Manufacturer
from src.catalog.product.domain.aggregates.product_type import ProductTypeAggregate
from src.catalog.product.infrastructure.models.product_type import ProductType
from src.uploads.domain.repository.upload_history import UploadHistoryRepository


class CategoryRelatedDataLoader:
    """
    Сервис для загрузки связанных данных для Category.
    
    Инкапсулирует работу с БД для загрузки:
    - UploadHistory (изображения)
    - Manufacturer (производитель)
    - Parent Category (родительская категория)
    """

    def __init__(
        self,
        db: AsyncSession,
        category_repository: CategoryRepository,
        upload_history_repository: UploadHistoryRepository,
    ):
        self.db = db
        self.category_repository = category_repository
        self.upload_history_repository = upload_history_repository

    async def get_upload_info(self, upload_id: int) -> tuple[int, str]:
        """
        Получить информацию о загруженном изображении.
        
        Returns:
            tuple[upload_id, object_key]
        """
        upload_record = await self.upload_history_repository.get(upload_id)
        
        if not upload_record:
            from src.catalog.category.domain.exceptions import CategoryInvalidImage
            raise CategoryInvalidImage(
                details={"reason": "upload_not_found", "upload_id": upload_id}
            )
        
        return upload_record.upload_id, upload_record.file_path

    async def get_manufacturer(self, manufacturer_id: int) -> Optional[ManufacturerAggregate]:
        """Получить ManufacturerAggregate по ID."""
        stmt = select(Manufacturer).where(Manufacturer.id == manufacturer_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        return ManufacturerAggregate(
            manufacturer_id=model.id,
            name=model.name,
            description=model.description,
        )

    async def get_parent_category(self, parent_id: int) -> Optional[CategoryAggregate]:
        """Получить родительскую CategoryAggregate по ID."""
        parent_agg = await self.category_repository.get(parent_id)

        if not parent_agg:
            return None

        return CategoryAggregate(
            category_id=parent_agg.id,
            name=parent_agg.name,
            description=parent_agg.description,
            parent_id=parent_agg.parent_id,
            manufacturer_id=parent_agg.manufacturer_id,
            device_type_id=parent_agg.device_type_id,
        )

    async def get_device_type(self, device_type_id: int) -> Optional[ProductTypeAggregate]:
        """Получить ProductTypeAggregate (device_type) по ID."""
        stmt = select(ProductType).where(ProductType.id == device_type_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return ProductTypeAggregate(
            product_type_id=model.id,
            name=model.name,
            parent_id=model.parent_id,
        )
