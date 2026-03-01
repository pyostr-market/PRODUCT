from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.uploads.application.dto.upload import UploadHistoryReadDTO
from src.uploads.infrastructure.models.upload_history import UploadHistory


class UploadHistoryReadRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, upload_id: int) -> Optional[UploadHistoryReadDTO]:
        stmt = select(UploadHistory).where(UploadHistory.id == upload_id)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._to_dto(model)

    def _to_dto(self, model: UploadHistory) -> UploadHistoryReadDTO:
        return UploadHistoryReadDTO(
            id=model.id,
            file_path=model.file_path,
            folder=model.folder,
            user_id=model.user_id,
            content_type=model.content_type,
            original_filename=model.original_filename,
            file_size=model.file_size,
            created_at=model.created_at.isoformat() if model.created_at else None,
        )
