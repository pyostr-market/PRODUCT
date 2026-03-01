from abc import ABC, abstractmethod
from typing import Optional

from src.uploads.domain.aggregates.upload_history import UploadHistoryAggregate


class UploadHistoryRepository(ABC):

    @abstractmethod
    async def get(self, upload_id: int) -> Optional[UploadHistoryAggregate]:
        """Получить запись о загрузке по ID."""
        pass

    @abstractmethod
    async def get_by_file_path(self, file_path: str) -> Optional[UploadHistoryAggregate]:
        """Получить запись о загрузке по пути к файлу."""
        pass

    @abstractmethod
    async def create(self, aggregate: UploadHistoryAggregate) -> UploadHistoryAggregate:
        """Создать запись о загрузке."""
        pass

    @abstractmethod
    async def delete(self, upload_id: int) -> bool:
        """Удалить запись о загрузке (без удаления файла из S3)."""
        pass
