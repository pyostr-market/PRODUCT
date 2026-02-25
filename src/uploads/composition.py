from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services.images.storage import S3ImageStorageService
from src.uploads.application.read_models.upload_read_repository import (
    UploadHistoryReadRepository,
)
from src.uploads.application.upload_service import UploadService
from src.uploads.infrastructure.orm.upload_history import (
    SqlAlchemyUploadHistoryRepository,
)


class UploadsComposition:
    """Composition root для модуля загрузок."""

    def __init__(self, db: AsyncSession):
        self.db = db

    def build_upload_service(self) -> UploadService:
        """Создать сервис загрузок."""
        return UploadService(
            upload_repository=SqlAlchemyUploadHistoryRepository(self.db),
            read_repository=UploadHistoryReadRepository(self.db),
            image_storage=S3ImageStorageService.from_settings(),
        )
