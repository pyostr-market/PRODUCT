from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.uploads.domain.aggregates.upload_history import UploadHistoryAggregate
from src.uploads.domain.repository.upload_history import UploadHistoryRepository
from src.uploads.infrastructure.models.upload_history import UploadHistory


class SqlAlchemyUploadHistoryRepository(UploadHistoryRepository):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, upload_id: int) -> Optional[UploadHistoryAggregate]:
        stmt = select(UploadHistory).where(UploadHistory.id == upload_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def get_by_file_path(self, file_path: str) -> Optional[UploadHistoryAggregate]:
        stmt = select(UploadHistory).where(UploadHistory.file_path == file_path)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_aggregate(model)

    async def create(self, aggregate: UploadHistoryAggregate) -> UploadHistoryAggregate:
        model = UploadHistory(
            user_id=aggregate.user_id,
            file_path=aggregate.file_path,
            folder=aggregate.folder,
            content_type=aggregate.content_type,
            original_filename=aggregate.original_filename,
            file_size=aggregate.file_size,
        )
        self.db.add(model)
        await self.db.flush()

        aggregate.upload_id = model.id
        return aggregate

    async def delete(self, upload_id: int) -> bool:
        model = await self.db.get(UploadHistory, upload_id)

        if not model:
            return False

        # Удаляем только запись из БД, файл в S3 остаётся
        await self.db.delete(model)
        return True

    @staticmethod
    def _to_aggregate(model: UploadHistory) -> UploadHistoryAggregate:
        return UploadHistoryAggregate(
            upload_id=model.id,
            user_id=model.user_id,
            file_path=model.file_path,
            folder=model.folder,
            content_type=model.content_type,
            original_filename=model.original_filename,
            file_size=model.file_size,
        )
