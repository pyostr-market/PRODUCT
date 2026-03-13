from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.catalog.manufacturer.application.dto.manufacturer import ManufacturerImageReadDTO, ManufacturerReadDTO
from src.catalog.manufacturer.infrastructure.models.manufacturer import Manufacturer
from src.catalog.manufacturer.infrastructure.models.manufacturer_image import ManufacturerImage
from src.uploads.infrastructure.models.upload_history import UploadHistory


class ManufacturerReadRepository:

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
            # Если S3 не настроен, возвращаем пустую строку
            return ""

    async def get_by_id(self, manufacturer_id: int) -> Optional[ManufacturerReadDTO]:
        stmt = (
            select(Manufacturer)
            .options(
                selectinload(Manufacturer.image)
                .selectinload(ManufacturerImage.upload)
            )
            .where(Manufacturer.id == manufacturer_id)
        )

        result = await self.db.execute(stmt)
        manufacturer = result.scalar_one_or_none()

        if not manufacturer:
            return None

        image_dto = None
        if manufacturer.image and manufacturer.image.upload:
            image_dto = ManufacturerImageReadDTO(
                upload_id=manufacturer.image.upload_id,
                image_url=self._build_image_url(manufacturer.image.upload.file_path),
            )

        return ManufacturerReadDTO(
            id=manufacturer.id,
            name=manufacturer.name,
            description=manufacturer.description,
            image=image_dto,
        )

    async def filter(
        self,
        name: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[List[ManufacturerReadDTO], int]:

        stmt = select(Manufacturer).options(
            selectinload(Manufacturer.image)
            .selectinload(ManufacturerImage.upload)
        )

        count_stmt = select(func.count()).select_from(Manufacturer)

        if name:
            stmt = stmt.where(Manufacturer.name.ilike(f"%{name}%"))
            count_stmt = count_stmt.where(
                Manufacturer.name.ilike(f"%{name}%")
            )

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        count_result = await self.db.execute(count_stmt)

        manufacturers = result.scalars().all()
        
        items = []
        for m in manufacturers:
            image_dto = None
            if m.image and m.image.upload:
                image_dto = ManufacturerImageReadDTO(
                    upload_id=m.image.upload_id,
                    image_url=self._build_image_url(m.image.upload.file_path),
                )
            items.append(ManufacturerReadDTO(
                id=m.id,
                name=m.name,
                description=m.description,
                image=image_dto,
            ))

        total = count_result.scalar() or 0
        return items, total
