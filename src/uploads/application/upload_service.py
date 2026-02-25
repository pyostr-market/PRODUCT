from dataclasses import dataclass
from typing import Optional

from src.core.services.images import ImageStorageService
from src.uploads.application.dto.upload import UploadCreateDTO, UploadHistoryReadDTO
from src.uploads.application.read_models.upload_read_repository import (
    UploadHistoryReadRepository,
)
from src.uploads.domain.aggregates.upload_history import UploadHistoryAggregate
from src.uploads.domain.repository.upload_history import UploadHistoryRepository


@dataclass
class UploadResult:
    upload_id: int
    file_path: str
    public_url: str


class UploadService:
    """Сервис для загрузки файлов в S3 и ведения истории загрузок."""

    def __init__(
        self,
        upload_repository: UploadHistoryRepository,
        read_repository: UploadHistoryReadRepository,
        image_storage: ImageStorageService,
    ):
        self.upload_repository = upload_repository
        self.read_repository = read_repository
        self.image_storage = image_storage

    async def upload_file(
        self,
        file_data: bytes,
        folder: str,
        filename: str,
        content_type: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> UploadResult:
        """
        Загрузить файл в S3 и создать запись в истории загрузок.

        Args:
            file_data: Байты файла
            folder: Папка для файла (products, categories, etc.)
            filename: Имя файла
            content_type: MIME тип файла
            user_id: ID пользователя

        Returns:
            UploadResult с ID загрузки, путём и публичным URL
        """
        # Генерируем уникальный ключ для файла
        file_key = self.image_storage.build_key(folder=folder, filename=filename)

        # Загружаем файл в S3
        await self.image_storage.upload_bytes(
            data=file_data,
            key=file_key,
            content_type=content_type,
        )

        # Создаём запись в истории загрузок
        aggregate = UploadHistoryAggregate(
            file_path=file_key,
            folder=folder,
            user_id=user_id,
            content_type=content_type,
            original_filename=filename,
            file_size=len(file_data),
        )

        created_aggregate = await self.upload_repository.create(aggregate)

        # Строим публичный URL
        public_url = self.image_storage.build_public_url(file_key)

        return UploadResult(
            upload_id=created_aggregate.upload_id,
            file_path=file_key,
            public_url=public_url,
        )

    async def get_upload(self, upload_id: int) -> Optional[UploadHistoryReadDTO]:
        """Получить информацию о загрузке по ID."""
        return await self.read_repository.get_by_id(upload_id)

    async def get_upload_by_path(self, file_path: str) -> Optional[UploadHistoryReadDTO]:
        """Получить информацию о загрузке по пути к файлу."""
        aggregate = await self.upload_repository.get_by_file_path(file_path)
        if not aggregate:
            return None
        return await self.read_repository.get_by_id(aggregate.upload_id)
